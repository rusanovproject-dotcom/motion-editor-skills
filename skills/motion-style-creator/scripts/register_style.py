#!/usr/bin/env python3
"""Add one QA-reviewed module; never overwrite an existing style or stale registry."""
import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tree_hash(folder):
    h = hashlib.sha256()
    for p in sorted(Path(folder).rglob('*')):
        if p.is_symlink():
            raise ValueError('Module symlinks are not supported')
        if p.is_file():
            h.update(p.relative_to(folder).as_posix().encode() + b'\0')
            h.update(p.read_bytes())
    return h.hexdigest()


def register(editor, module, expected, qa_path):
    editor, module = Path(editor).resolve(), Path(module).resolve()
    registry = editor / 'styles/registry.json'
    qa = json.loads(Path(qa_path).read_text())
    if qa.get('module_sha256') != tree_hash(module) or qa.get('reviewed') is not True:
        raise ValueError('QA must review this exact module tree')
    manifest = json.loads((module/'style.json').read_text())
    ident = manifest.get('id')
    if not isinstance(ident, str) or not ident or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in ident) or '/' in ident:
        raise ValueError('Invalid module id')
    # Actual validation below uses the editor contract; this precheck keeps paths local.
    expected_layouts = set(manifest.get('capabilities', []))
    renders = qa.get('renders', [])
    for layout in expected_layouts:
        samples = [x for x in renders if x.get('layout') == layout]
        if len({x.get('topic') for x in samples}) < 2:
            raise ValueError('QA needs two distinct topics per supported layout')
        for sample in samples:
            video = Path(sample['path'])
            if sample.get('sha256') != digest(video):
                raise ValueError('Rendered video changed since QA')
            probe = subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,duration','-of','json',str(video)], check=True, capture_output=True, text=True)
            streams = json.loads(probe.stdout).get('streams', [])
            if not streams or float(streams[0].get('duration',0)) <= 0:
                raise ValueError('QA render has no video duration')
    spec = importlib.util.spec_from_file_location('editor_registry', editor/'scripts/style_registry.py')
    contract = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(contract)
    lock_path = editor/'styles/.registration.lock'
    with lock_path.open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if digest(registry) != expected:
            raise ValueError('Registry changed; re-read and revalidate before retry')
        before = registry.read_bytes()
        data = json.loads(before)
        relative = ident+'/style.json'
        target = editor/'styles'/ident
        if target.exists() or target.is_symlink() or relative in data['styles']:
            raise ValueError('Existing module is never overwritten')
        # Validate the candidate merged registry without writing the live module.
        with tempfile.TemporaryDirectory(prefix='motion-style-') as tmp:
            scratch = Path(tmp)
            shutil.copytree(editor/'styles', scratch/'styles')
            shutil.copytree(module, scratch/'styles'/ident)
            data['styles'].append(relative)
            (scratch/'styles/registry.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
            contract.load_registry(scratch)
            # Copy first; then an atomic registry replacement makes it discoverable.
            staged = Path(tempfile.mkdtemp(prefix='.pending-style-', dir=editor/'styles'))
            try:
                shutil.copytree(module, staged/'module')
                if tree_hash(staged/'module') != qa['module_sha256']:
                    raise ValueError('Module changed during registration')
                if registry.read_bytes() != before:
                    raise ValueError('Registry changed during preparation')
                os.rename(staged/'module', target)
                try:
                    pending = staged/'registry.json'
                    pending.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
                    os.replace(pending, registry)
                except BaseException:
                    # Only our new folder; never restore a whole old registry over others.
                    shutil.rmtree(target)
                    raise
            finally:
                shutil.rmtree(staged)
    return {'registered': ident, 'registry_sha256': digest(registry), 'module_sha256': qa['module_sha256']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--editor',type=Path,required=True)
    p.add_argument('--module',type=Path,required=True)
    p.add_argument('--registry-sha',required=True)
    p.add_argument('--qa',type=Path,required=True)
    a=p.parse_args()
    try:
        print(json.dumps(register(a.editor,a.module,a.registry_sha,a.qa),ensure_ascii=False,indent=2))
    except (ValueError,OSError,KeyError,TypeError,subprocess.CalledProcessError) as e:
        p.exit(1,'ERROR: '+str(e)+'\n')

if __name__=='__main__': main()
