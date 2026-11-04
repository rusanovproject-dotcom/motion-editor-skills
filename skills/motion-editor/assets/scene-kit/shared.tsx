import React from 'react';
import {AbsoluteFill, Img, Video, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

export type SceneConfig = {
  style: string;
  width: number; height: number; fps: number; duration: number;
  title: string; subtitle: string; labels: string[]; accent: string;
  layout: 'fullscreen'|'lower-panel';
  panel?: {x:number;y:number;width:number;height:number};
  backgroundVideo?: string;
  images?: string[];
};
export const sans='"Helvetica Neue", Arial, sans-serif';
export const mono='Menlo, Consolas, monospace';
export const condensed='Impact, "Arial Narrow", Arial, sans-serif';
export const clamp=(v:number)=>Math.max(0,Math.min(1,v));
export const mix=(v:number,a:number,b:number)=>a+(b-a)*v;
export const smooth=(t:number)=>{const x=clamp(t); return 1-Math.pow(1-x,3);};
export const appear=(frame:number,start:number,fps:number)=>spring({frame:frame-start,fps,config:{damping:17,stiffness:160,mass:.8}});
export const noise=(i:number)=>{const x=Math.sin(i*127.1+311.7)*43758.5453;return x-Math.floor(x);};
export const localAsset=(src:string)=>{if (/^data:image\//i.test(src)) return src; if (/^[a-z]+:|^[/\\]|(^|[/\\])\.\.([/\\]|$)/i.test(src)) throw new Error('Use a local project-public asset; remote and parent paths are not allowed'); return staticFile(src);};

export const Arrow:React.FC<{color:string;progress:number}>=({color,progress})=><svg width="180" height="70" viewBox="0 0 180 70"><path d="M10 35 H150 M130 15 L152 35 L130 55" stroke={color} strokeWidth="7" fill="none" strokeDasharray="220" strokeDashoffset={220*(1-clamp(progress))}/></svg>;
export const Star:React.FC<{size?:number;color?:string}>=({size=130,color='#111'})=><svg width={size} height={size} viewBox="0 0 100 100"><path d="M50 0 Q55 35 100 30 Q70 50 92 90 Q55 66 25 100 Q37 62 0 40 Q40 42 50 0" fill={color}/></svg>;
export const Grain:React.FC<{light?:boolean}>=({light=false})=><AbsoluteFill style={{pointerEvents:'none',opacity:light?.12:.17,mixBlendMode:light?'multiply':'screen'}}><svg width="100%" height="100%"><filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".68" numOctaves="3" seed="42" stitchTiles="stitch"/></filter><rect width="100%" height="100%" filter="url(#grain)" opacity=".35"/></svg></AbsoluteFill>;
export const Check:React.FC<{color?:string}>=({color='#4263eb'})=><svg width="80" height="80" viewBox="0 0 80 80"><circle cx="40" cy="40" r="36" fill={color}/><path d="M22 40 L35 53 L59 27" stroke="white" strokeWidth="6" fill="none" strokeLinecap="round" strokeLinejoin="round"/></svg>;


export type StyleSceneProps = {c: SceneConfig; f: number; span: number; compact: boolean};
