import React from 'react';
import {AbsoluteFill, Video, useCurrentFrame, useVideoConfig} from 'remotion';
import {SceneConfig, StyleSceneProps, localAsset} from './shared';
export type {SceneConfig, StyleSceneProps} from './shared';

// The core owns placement and media, never a style's typography or choreography.
export const SceneKit: React.FC<{config: SceneConfig; renderer: React.ComponentType<StyleSceneProps>}> = ({config:c, renderer:Renderer}) => {
  const f=useCurrentFrame(); const {width,height,durationInFrames}=useVideoConfig();
  const lower=c.layout==='lower-panel';
  const panel=c.panel||{x:.05,y:.58,width:.9,height:.34};
  const bounds=lower?{left:panel.x*width,top:panel.y*height,width:panel.width*width,height:panel.height*height}:{left:0,top:0,width,height};
  const designHeight=lower?720:1920;
  return <AbsoluteFill style={{background:lower?'transparent':'#111'}}>
    {c.backgroundVideo&&<Video src={localAsset(c.backgroundVideo)} style={{position:'absolute',width:'100%',height:'100%',objectFit:'cover'}}/>}
    <div style={{position:'absolute',...bounds,overflow:'hidden'}}><div style={{position:'absolute',width:1080,height:designHeight,transform:`scale(${bounds.width/1080},${bounds.height/designHeight})`,transformOrigin:'top left'}}><Renderer c={c} f={f} span={durationInFrames} compact={lower}/></div></div>
  </AbsoluteFill>;
};
