#!/usr/bin/env python3
"""Validate timing and normalized placement; this does not inspect rendered pixels."""
import argparse
import json
import math
from pathlib import Path
import sys


def number(x):
    return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)


def box_ok(b):
    return isinstance(b,list) and len(b)==4 and all(number(n) for n in b) and b[0]>=0 and b[1]>=0 and b[2]>0 and b[3]>0 and b[0]+b[2]<=1.00000001 and b[1]+b[3]<=1.00000001


def intersects(a,b):
    return a[0]<b[0]+b[2] and a[0]+a[2]>b[0] and a[1]<b[1]+b[3] and a[1]+a[3]>b[1]


def check(plan):
    errors=[];warnings=[]
    for k in ['width','height','fps','duration']:
        if not number(plan.get(k)) or plan[k]<=0:
            errors.append(f'{k}: must be positive finite number')
    if plan.get('timebase')!='output': errors.append('timebase: must be output')
    timing=plan.get('timing_status')
    if timing not in ['confirmed','provisional']: errors.append('timing_status: expected confirmed|provisional')
    if timing=='provisional': warnings.append('не синхронизировано: timing_status=provisional')
    protected=plan.get('protected_regions',[])
    if not isinstance(protected,list):
        errors.append('protected_regions must be an array');protected=[]
    valid_regions=[]
    for i,r in enumerate(protected):
        if not isinstance(r,dict) or not box_ok(r.get('box')): errors.append(f'protected_regions[{i}]: invalid box')
        else:valid_regions.append(r)
    scenes=plan.get('scenes')
    if not isinstance(scenes,list) or not scenes:
        errors.append('scenes must be a nonempty array');scenes=[]
    ids=set()
    for i,s in enumerate(scenes):
        prefix=f'scenes[{i}]'
        if not isinstance(s,dict):errors.append(prefix+': expected object');continue
        ident=s.get('id')
        if not isinstance(ident,str) or not ident.strip() or ident in ids:errors.append(prefix+': missing/duplicate id')
        else:ids.add(ident)
        start,end=s.get('start'),s.get('end')
        if not number(start) or not number(end) or start<0 or end<=start or (number(plan.get('duration')) and end>plan['duration']):errors.append(prefix+': invalidrange')
        b=s.get('box');valid_box=box_ok(b)
        if not valid_box:errors.append(prefix+': outsideframe or invalid box')
        layout=s.get('layout')
        if layout not in ['fullscreen-insert','overlay','lower-panel','side-panel']:errors.append(prefix+': invalid layout')
        if layout=='fullscreen-insert':
            if plan.get('allow_fullscreen') is not True:errors.append(prefix+': fullscreen requires allow_fullscreen=true')
        elif valid_box:
            for r in valid_regions:
                if intersects(b,r['box']):errors.append(prefix+': face/protected intersection '+str(r.get('id','unnamed')))
        for field in ['meaning','action','style']:
            if not isinstance(s.get(field),str) or not s[field].strip():errors.append(prefix+': missing '+field)
        anchor=s.get('anchor')
        if not isinstance(anchor,dict): errors.append(prefix+': anchor must be object')
        else:
            if anchor.get('timebase')!='output':errors.append(prefix+': anchor timebase must be output')
            if anchor.get('status') not in ['confirmed','provisional']:errors.append(prefix+': invalid anchor status')
            if timing=='confirmed' and anchor.get('status')!='confirmed':errors.append(prefix+': confirmed timing with provisional anchor')
            if not isinstance(anchor.get('phrase'),str) or not anchor['phrase'].strip():errors.append(prefix+': anchor phrase missing')
            if not isinstance(anchor.get('occurrence'),int) or isinstance(anchor.get('occurrence'),bool) or anchor['occurrence']<1:errors.append(prefix+': occurrence must be positive integer')
        assets=s.get('assets',[])
        if not isinstance(assets,list):errors.append(prefix+': assets must be array')
        else:
            for a in assets:
                if not isinstance(a,dict) or not a.get('id') or a.get('status') not in ['exact','approximation','missing']:errors.append(prefix+': invalid asset status/id')
                elif a['status'] in ['approximation','missing']:warnings.append(prefix+': asset '+a['id']+' is '+a['status'])
        if not isinstance(s.get('verification'),list) or not s['verification'] or not all(isinstance(v,str) and v.strip() for v in s['verification']):errors.append(prefix+': verification must contain checks')
    return {'ok':not errors,'errors':errors,'warnings':warnings,'scope':'JSON timing and bounding boxes only; no visual, speech or sound verification'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('plan',type=Path);a=p.parse_args()
    try:
        value=json.loads(a.plan.read_text());result=check(value) if isinstance(value,dict) else {'ok':False,'errors':['Top-level plan must be an object'],'warnings':[]}
    except (OSError,ValueError) as e: print(f'ERROR: {e}',file=sys.stderr);return 2
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['ok'] else 1
if __name__=='__main__':raise SystemExit(main())
