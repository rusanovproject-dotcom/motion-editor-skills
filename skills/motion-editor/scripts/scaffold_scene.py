#!/usr/bin/env python3
"""Scaffold an editable offline Remotion scene using an existing local engine."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import shlex
import shutil
import sys

import importlib.util

_registry_spec = importlib.util.spec_from_file_location('motion_style_registry', Path(__file__).with_name('style_registry.py'))
_registry = importlib.util.module_from_spec(_registry_spec)
_registry_spec.loader.exec_module(_registry)



def scaffold(project,engine,style,width=1080,height=1920,fps=30,duration=6,browser_executable=None):
    project=Path(project).expanduser().resolve()
    engine=Path(engine).expanduser().resolve(strict=True)
    root = Path(__file__).resolve().parent.parent
    styles = _registry.load_registry(root)
    routed = _registry.resolve_style(styles, explicit=style)
    if routed['status'] != 'selected':
        raise ValueError('Unknown or ambiguous style: '+str(style))
    style = routed['style_id']
    selected = styles[style]
    if width < 64 or height < 64 or width%2 or height%2:
        raise ValueError('width/height must be even integers >=64')
    if not math.isfinite(fps) or fps <= 0 or fps > 120:
        raise ValueError('fps must be finite, >0 and <=120')
    if not math.isfinite(duration) or duration <= 0 or duration > 600:
        raise ValueError('duration must be finite, >0 and <=600')
    if project.exists() and (not project.is_dir() or any(project.iterdir())):
        raise ValueError('Project exists and is not empty; choose a new project directory')
    dependencies=engine/'node_modules'
    cli=dependencies/'.bin/remotion'
    if not cli.is_file() or not (dependencies/'remotion/package.json').is_file():
        raise ValueError('Engine must already contain installed Remotion and @remotion/cli')
    kit=Path(__file__).resolve().parent.parent/'assets/scene-kit'
    if not (kit/'SceneKit.tsx').is_file():
        raise ValueError('Bundled scene-kit is missing')
    project.mkdir(parents=True,exist_ok=True)
    shutil.copytree(kit, project/'assets/scene-kit')
    shutil.copy2(kit/'entry.tsx',project/'entry.tsx')
    imports = ["import React from 'react';", "import {SceneKit as Core} from './assets/scene-kit/SceneKit';", "import {SceneConfig, StyleSceneProps} from './assets/scene-kit/shared';", "export type {SceneConfig} from './assets/scene-kit/shared';"]
    entries=[]; capabilities={}
    for index,(ident,module) in enumerate(styles.items()):
        target=project/'styles'/ident
        shutil.copytree(module['_folder'],target,ignore=shutil.ignore_patterns('__pycache__','*.pyc','node_modules'))
        renderer_rel=str(Path('styles')/ident/module['_renderer'].relative_to(module['_folder'])).replace('\\','/')
        imports.append('import {StyleScene as Style'+str(index)+'} from '+json.dumps('./'+renderer_rel)+';')
        entries.append(json.dumps(ident)+':Style'+str(index))
        capabilities[ident]=module['capabilities']
    wrapper='\n'.join(imports)+'\nconst renderers: Record<string,React.ComponentType<StyleSceneProps>>={'+','.join(entries)+'};\n'
    wrapper+='const capabilities: Record<string,string[]>='+json.dumps(capabilities)+';\n'
    wrapper+='export const isKnownStyle=(id:string)=>Object.prototype.hasOwnProperty.call(renderers,id);\n'
    wrapper+='export const SceneKit:React.FC<SceneConfig>=(c)=>{if(!isKnownStyle(c.style))throw new Error("Unknown scene style");if(!capabilities[c.style].includes(c.layout))throw new Error("Style does not support this layout");return <Core config={c} renderer={renderers[c.style]}/>;};\n'
    (project/'SceneKit.tsx').write_text(wrapper)

    (project/'public').mkdir()
    (project/'node_modules').symlink_to(dependencies,target_is_directory=True)
    layout=selected['defaults'].get('layout', 'fullscreen' if 'fullscreen' in selected['capabilities'] else selected['capabilities'][0])
    default={'title':'Идея становится продуктом','subtitle':'Смысл → действие → результат','labels':['Идея','Продукт','Готово'],'accent':'#4263eb',**selected['defaults'],'style':style,'width':width,'height':height,'fps':fps,'duration':duration,'layout':layout}
    (project/'scene.json').write_text(json.dumps(default,ensure_ascii=False,indent=2)+'\n')
    # Pin the browser path when already installed: do not use browser ensure,
    # npx, npm, or any command that could download during this scaffold.
    browsers=list((dependencies/'.remotion').glob('chrome-headless-shell/**/chrome-headless-shell'))
    browser=Path(browser_executable).expanduser().resolve(strict=True) if browser_executable else next((b for b in browsers if b.is_file()),None)
    if browser is not None and not browser.is_file():
        raise ValueError('browser-executable must be an existing executable file')
    cmd=[str(cli),'render','entry.tsx','MotionScene']
    if browser:
        cmd+=['--browser-executable',str(browser)]
    guard=('test -x '+shlex.quote(str(browser))+' || { echo "Local browser is unavailable; no download was attempted" >&2; exit 3; }\n') if browser else 'echo "No local browser found. Re-scaffold with --browser-executable pointing to an installed Chromium. No download was attempted." >&2\nexit 3\n'
    script='#!/bin/sh\nset -eu\n'+guard+'cd '+shlex.quote(str(project))+'''\noutput=${1:-out.mp4}\nif [ "$#" -gt 0 ]; then shift; fi\ncase "$output" in\n  *.mov) codec=prores; set -- --image-format=png --pixel-format=yuva444p10le --prores-profile=4444 "$@" ;;\n  *.webm) codec=vp9; set -- --image-format=png --pixel-format=yuva420p "$@" ;;\n  *.mp4) codec=h264 ;;\n  *) echo "Use .mp4, .mov or .webm output" >&2; exit 2 ;;\nesac\nexec '''+shlex.join(cmd[:4])+''' "$output" --codec="$codec" --concurrency=2 --log=error '''+shlex.join(cmd[4:])+''' "$@"\n'''
    (project/'render.sh').write_text(script)
    (project/'render.sh').chmod(0o755)
    (project/'package.json').write_text(json.dumps({'name':'motion-editor-scene','private':True,'scripts':{'render':'sh render.sh'},'description':'Editable scene; dependencies are linked to an existing local engine, not installed here.'},indent=2)+'\n')
    return {'project':str(project),'scene':str(project/'scene.json'),'render_command':shlex.join(['sh',str(project/'render.sh')]),'browser_found':bool(browser),'note':'Starter motion scene, not a faithful reconstruction. Review and adapt source to the supplied reference.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path)
    p.add_argument('--engine-root',type=Path)
    p.add_argument('--style',help='Registered style id or alias; see --list-styles')
    p.add_argument('--list-styles',action='store_true')
    p.add_argument('--width',type=int,default=1080)
    p.add_argument('--height',type=int,default=1920)
    p.add_argument('--fps',type=float,default=30)
    p.add_argument('--duration',type=float,default=6)
    p.add_argument('--browser-executable',type=Path,help='Existing local Chromium executable; never downloaded')
    a=p.parse_args()
    try:
        if a.list_styles:
            print(json.dumps({'styles':[_registry.public_style(s) for s in _registry.load_registry().values()]},ensure_ascii=False,indent=2))
            return 0
        if not a.project or not a.engine_root or not a.style:
            p.error('--project, --engine-root and --style are required unless --list-styles')
        result=scaffold(a.project,a.engine_root,a.style,a.width,a.height,a.fps,a.duration,a.browser_executable)
    except (ValueError,OSError) as e:
        print(f'ERROR: {e}',file=sys.stderr)
        return 1
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
