#!/usr/bin/env python3
"""Discover and route independently versioned local motion style modules."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys

ID = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$')
DEFAULT_ROOT = Path(__file__).resolve().parent.parent


def normalize(value):
    return re.sub(r'[^\w]+', ' ', value.casefold(), flags=re.UNICODE).strip()


def contained_file(base, value):
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError('Module paths must be nonempty relative paths')
    base = base.resolve()
    target = (base / value).resolve()
    if not target.is_relative_to(base) or not target.is_file():
        raise ValueError(f'Missing or escaping module file: {value}')
    return target


def load_registry(root=DEFAULT_ROOT):
    root = Path(root).resolve()
    registry = json.loads((root/'styles/registry.json').read_text())
    if not isinstance(registry, dict) or registry.get('schema_version') != 1 or not isinstance(registry.get('styles'), list) or not registry['styles']:
        raise ValueError('Invalid or empty styles/registry.json')
    found = {}; aliases = {}
    for rel in registry['styles']:
        manifest_path = contained_file(root/'styles', rel)
        manifest = json.loads(manifest_path.read_text())
        if not isinstance(manifest, dict) or manifest.get('schema_version') != 1:
            raise ValueError(f'Invalid style manifest: {rel}')
        ident = manifest.get('id')
        if not isinstance(ident, str) or not ID.fullmatch(ident) or ident in found:
            raise ValueError(f'Invalid or duplicate style id: {ident}')
        if not isinstance(manifest.get('name'), str) or not manifest['name'].strip():
            raise ValueError(f'{ident}: missing display name')
        for key in ['aliases', 'keywords']:
            if not isinstance(manifest.get(key, []), list) or not all(isinstance(x,str) and normalize(x) for x in manifest.get(key, [])):
                raise ValueError(f'{ident}: {key} must contain nonempty strings')
        if not isinstance(manifest.get('defaults'), dict):
            raise ValueError(f'{ident}: defaults must be an object')
        defaults = manifest['defaults']
        for key in ['title', 'subtitle', 'accent']:
            if key in defaults and not isinstance(defaults[key], str):
                raise ValueError(f'{ident}: defaults.{key} must be a string')
        if 'accent' in defaults and not defaults['accent'].strip():
            raise ValueError(f'{ident}: defaults.accent must not be empty')
        if 'labels' in defaults and (not isinstance(defaults['labels'], list) or len(defaults['labels']) < 3 or not all(isinstance(x,str) for x in defaults['labels'])):
            raise ValueError(f'{ident}: defaults.labels must contain at least three strings')
        caps = manifest.get('capabilities')
        if not isinstance(caps, list) or not caps or not all(isinstance(x,str) and x in ['fullscreen','lower-panel'] for x in caps) or len(set(caps)) != len(caps):
            raise ValueError(f'{ident}: capabilities must list unique supported layouts (fullscreen, lower-panel)')
        if 'layout' in defaults and defaults['layout'] not in caps:
            raise ValueError(f'{ident}: defaults.layout is not supported by this style')
        folder = manifest_path.parent
        skill = contained_file(folder, manifest.get('skill'))
        renderer = contained_file(folder, manifest.get('renderer'))
        if skill.suffix != '.md' or renderer.suffix not in ['.tsx','.jsx','.ts','.js']:
            raise ValueError(f'{ident}: invalid skill or renderer file type')
        for alias in [ident, *manifest.get('aliases', [])]:
            norm = normalize(alias)
            if norm in aliases and aliases[norm] != ident:
                raise ValueError(f'Alias collision: {alias} ({aliases[norm]}, {ident})')
            aliases[norm] = ident
        found[ident] = dict(manifest, _folder=folder, _manifest=manifest_path, _skill=skill, _renderer=renderer)
    return found


def public_style(style):
    return {k:v for k,v in style.items() if not k.startswith('_')}


def match_reference(value, styles):
    name = Path(value.replace('\\','/')).name
    names = {normalize(name), normalize(Path(name).stem)}
    return {s['id'] for s in styles.values() if names.intersection(normalize(a) for a in [s['id'], *s.get('aliases', [])])}


def resolve_style(styles, explicit=None, references=(), query=''):
    if explicit:
        norm = normalize(explicit)
        hits = {s['id'] for s in styles.values() if norm in {normalize(a) for a in [s['id'], *s.get('aliases', [])]}}
        if not hits:
            hits = match_reference(explicit, styles)
        return decision(hits, 'explicit', explicit)
    hits = set()
    for ref in references:
        hits.update(match_reference(ref, styles))
    if hits:
        return decision(hits, 'reference', list(references))
    norm = normalize(query)
    hits = set()
    for s in styles.values():
        for word in [s['id'], *s.get('aliases', []), *s.get('keywords', [])]:
            phrase = normalize(word)
            if re.search(r'(?<!\w)'+re.escape(phrase)+r'(?!\w)', norm):
                hits.add(s['id']); break
    return decision(hits, 'query' if hits else 'none', query)


def decision(hits, reason, supplied):
    candidates = sorted(hits)
    return {'status':'selected' if len(candidates)==1 else 'ambiguous' if candidates else 'unknown_style' if reason=='explicit' else 'needs_style', 'style_id':candidates[0] if len(candidates)==1 else None, 'candidates':candidates, 'reason':reason, 'input':supplied}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=DEFAULT_ROOT)
    p.add_argument('--style')
    p.add_argument('--reference-name',action='append',default=[])
    p.add_argument('--query',default='')
    p.add_argument('--list',action='store_true')
    p.add_argument('--validate',action='store_true')
    a=p.parse_args()
    try:
        styles=load_registry(a.root)
        if a.list or a.validate:
            result={'ok':True,'styles':[public_style(s) for s in styles.values()]}
        else:
            result=resolve_style(styles,a.style,a.reference_name,a.query)
            if result['style_id']:
                s=styles[result['style_id']]
                result.update(skill=str(s['_skill'].relative_to(a.root.resolve())), renderer=str(s['_renderer'].relative_to(a.root.resolve())))
    except (OSError,ValueError,TypeError) as exc:
        print(json.dumps({'ok':False,'error':str(exc)},ensure_ascii=False));return 1
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if a.list or a.validate or result['status']=='selected' else 2

if __name__=='__main__':raise SystemExit(main())
