#!/usr/bin/env python3
"""Create a local contact sheet plus an explicit timestamp index; no uploads."""
from __future__ import annotations
import argparse
import bisect
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def inspect(source: Path, output: Path, step=2.0, start=0.0, duration=None, fps=None):
    source = source.expanduser().resolve(strict=True)
    output = output.expanduser().resolve()
    if not source.is_file():
        raise ValueError('Input must be a local file')
    if not math.isfinite(start) or start < 0 or not math.isfinite(step) or step <= 0:
        raise ValueError('start must be non-negative; step must be positive and finite')
    if fps is not None and (not math.isfinite(fps) or fps <= 0):
        raise ValueError('fps must be positive and finite')
    if duration is not None and (not math.isfinite(duration) or duration <= 0):
        raise ValueError('duration must be positive and finite')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output directory is not empty; choose a new directory')
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        raise ValueError('ffmpeg and ffprobe must already be installed')
    meta = json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(source)]).stdout)
    video = next((s for s in meta['streams'] if s['codec_type'] == 'video'), None)
    if video is None:
        raise ValueError('Input has no video stream')
    total = float(meta['format']['duration'])
    if start >= total:
        raise ValueError('start is outside video')
    end = min(total, start + duration) if duration is not None else total
    interval = 1 / fps if fps is not None else step
    count = max(1, math.ceil((end-start) / interval - 1e-9))
    if count > 120:
        raise ValueError('More than 120 samples; narrow the range or use a larger step')
    cell_width = 240
    cell_height = round(cell_width * video['height'] / video['width'])
    frame_info = json.loads(run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','json',str(source)]).stdout)
    frame_times = sorted(float(v['best_effort_timestamp_time']) for v in frame_info.get('frames',[]) if 'best_effort_timestamp_time' in v)
    if not frame_times:
        raise ValueError('No video-frame timestamps available for this input')
    requested_times = [start + i * interval for i in range(count)]
    sample_times = []
    skipped_times = []
    for timestamp in requested_times:
        idx = bisect.bisect_left(frame_times, timestamp - 1e-8)
        # Container/audio duration can extend beyond the last actual video frame.
        # Do not seek a nonexistent frame or label it as the previous one.
        if idx >= len(frame_times) or frame_times[idx] >= end:
            skipped_times.append(timestamp)
        else:
            sample_times.append(timestamp)
    if not sample_times:
        raise ValueError('No video frames exist at or after the requested times within this range')
    count = len(sample_times)
    columns = min(6, count) if fps is not None else min(4, count)
    rows = math.ceil(count / columns)
    output.mkdir(parents=True, exist_ok=True)
    frames = output / 'frames'
    frames.mkdir()
    index=[]
    # Individual seeks make the requested sampling times explicit. Decode from the
    # nearest preceding keyframe; ffmpeg chooses the frame at the requested time.
    for i, timestamp in enumerate(sample_times):
        dest=frames / f'{i:04d}.jpg'
        run(['ffmpeg','-hide_banner','-loglevel','error','-n','-ss',f'{timestamp:.9f}','-i',str(source),'-frames:v','1','-vf',f'scale={cell_width}:{cell_height}','-update','1',str(dest)])
        if not dest.is_file() or dest.stat().st_size == 0:
            raise ValueError(f'No decoded image was produced at {timestamp:.9f}s; inspect the video timestamps')
        frame_idx = min(bisect.bisect_left(frame_times, timestamp - 1e-8), len(frame_times)-1) if frame_times else None
        index.append({'cell':i,'row':i//columns,'column':i%columns,'requested_seconds':timestamp,'source_frame_seconds':frame_times[frame_idx] if frame_idx is not None else None,'source_frame_index':frame_idx,'frame_file':str(dest.relative_to(output))})
    run(['ffmpeg','-hide_banner','-loglevel','error','-n','-framerate','1','-i',str(frames/'%04d.jpg'),'-vf',f'tile={columns}x{rows}:padding=4:margin=4:color=gray','-frames:v','1','-update','1',str(output/'contact-sheet.jpg')])
    (output/'metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2)+'\n')
    manifest={'input_name':source.name,'start':start,'end':end,'interval':interval,'columns':columns,'rows':rows,'timestamp_kind':'requested media time plus ffprobe first frame at/after it; not a speech anchor','last_video_frame_seconds':frame_times[-1],'skipped_unavailable_times':skipped_times,'samples':index}
    (output/'index.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True,type=Path)
    p.add_argument('--output-dir',required=True,type=Path)
    p.add_argument('--step',type=float,default=2.0)
    p.add_argument('--start',type=float,default=0.0)
    p.add_argument('--duration',type=float)
    p.add_argument('--fps',type=float)
    a=p.parse_args()
    try:
        result=inspect(a.input,a.output_dir,a.step,a.start,a.duration,a.fps)
    except (ValueError,OSError,subprocess.CalledProcessError,KeyError,StopIteration) as e:
        print(f'ERROR: {e}',file=sys.stderr)
        return 1
    print(json.dumps({'output':str(a.output_dir.resolve()),'samples':len(result['samples'])}))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
