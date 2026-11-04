import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent.parent/'skills/motion-editor'

def load(name):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

class RuntimeTests(unittest.TestCase):
 def test_plan_detects_face_and_bad_anchor(self):
  check=load('check_plan').check
  plan={'width':1080,'height':1920,'fps':30,'duration':4,'timebase':'output','timing_status':'confirmed','protected_regions':[{'id':'face','box':[.2,.1,.6,.4]}],'scenes':[{'id':'s','start':0,'end':4,'anchor':{'phrase':'идея','occurrence':1,'timebase':'output','status':'provisional'},'meaning':'идея становится действием','action':'карточка превращается в продукт','style':'clean-editorial','layout':'overlay','box':[.3,.2,.2,.2],'assets':[],'verification':['проверить стыки']} ]}
  result=check(plan)
  self.assertTrue(any('intersection' in e for e in result['errors']))
  self.assertTrue(any('provisional anchor' in e for e in result['errors']))
  plan['timing_status']='provisional';plan['scenes'][0]['box']=[.1,.6,.8,.3]
  self.assertTrue(check(plan)['ok'])
  self.assertTrue(any('не синхронизировано' in w for w in check(plan)['warnings']))
 def test_scaffold_refuses_nonempty_and_no_browser_download(self):
  scaffold=load('scaffold_scene').scaffold
  with tempfile.TemporaryDirectory() as td:
   base=Path(td);engine=base/'engine';(engine/'node_modules/.bin').mkdir(parents=True);(engine/'node_modules/remotion').mkdir();(engine/'node_modules/remotion/package.json').write_text('{}');cli=engine/'node_modules/.bin/remotion';cli.write_text('#!/bin/sh\necho INVOKED\nexit 99\n');cli.chmod(0o755)
   project=base/'demo'
   result=scaffold(project,engine,'clean-editorial',540,960,30,4)
   self.assertFalse(result['browser_found'])
   p=subprocess.run(['sh',str(project/'render.sh')],capture_output=True,text=True)
   self.assertEqual(p.returncode,3);self.assertNotIn('INVOKED',p.stdout);self.assertIn('No download',p.stderr)
   marker=project/'scene.json';before=marker.read_bytes()
   with self.assertRaises(ValueError):scaffold(project,engine,'clean-editorial')
   self.assertEqual(marker.read_bytes(),before)
 def test_inspection_actual_pts_and_collision(self):
  inspect=load('inspect_reference').inspect
  with tempfile.TemporaryDirectory() as td:
   base=Path(td);video=base/'sample.mp4'
   subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','lavfi','-i','color=c=blue:s=120x200:r=10:d=2','-c:v','libx264','-pix_fmt','yuv420p',str(video)],check=True)
   result=inspect(video,base/'inspection',start=.5,duration=.5,fps=5)
   self.assertEqual(len(result['samples']),3)
   for i,r in enumerate(result['samples']):
    self.assertAlmostEqual(r['requested_seconds'],.5+i*.2)
    self.assertAlmostEqual(r['source_frame_seconds'],.5+i*.2)
   with self.assertRaises(ValueError):inspect(video,base/'inspection')
 def test_audio_tail_never_creates_a_phantom_video_frame(self):
  inspect=load('inspect_reference').inspect
  with tempfile.TemporaryDirectory() as td:
   base=Path(td);video=base/'audio-tail.mp4';out=base/'inspection'
   subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','lavfi','-i','color=c=blue:s=120x200:r=10:d=2','-f','lavfi','-i','anullsrc=r=48000:cl=mono','-t','2.2','-c:v','libx264','-c:a','aac','-pix_fmt','yuv420p',str(video)],check=True)
   result=inspect(video,out,start=1.8,duration=.4,fps=5)
   self.assertEqual(len(result['samples']),1)
   self.assertEqual(result['skipped_unavailable_times'],[2.0])
   for sample in result['samples']:
    self.assertTrue((out/sample['frame_file']).is_file())
    self.assertLessEqual(sample['requested_seconds'],result['last_video_frame_seconds'])
   with self.assertRaisesRegex(ValueError,'No video frames'):
    inspect(video,base/'after-video',start=2.05,duration=.1,fps=5)

if __name__=='__main__':unittest.main(verbosity=2)
