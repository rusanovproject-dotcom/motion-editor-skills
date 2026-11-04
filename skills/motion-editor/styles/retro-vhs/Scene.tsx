import React from 'react';
import {AbsoluteFill, useVideoConfig} from 'remotion';
import {StyleSceneProps, condensed, mono, appear, smooth, noise, Star} from '../../assets/scene-kit/shared';

export const StyleScene:React.FC<StyleSceneProps> = ({c,f,span,compact}) => {
  const {fps}=useVideoConfig(); const p=f/span;const a=appear(f,span*.08,fps);
  const zoom=1+smooth((p-.37)/.18)*.2;
  const bodyY=compact?160:550; const unitScale=compact?.55:1;
  const eyeBlink=Math.floor(f/(fps*.55))%3===0;
  const count=Math.floor(smooth((p-.55)/.3)*100);
  return <AbsoluteFill style={{background:'#230239',overflow:'hidden',fontFamily:condensed,color:'#fff'}}>
    <div style={{position:'absolute',width:2600,height:2600,left:-760,top:compact?-900:-560,background:'repeating-conic-gradient(from 0deg,#4c0766 0deg 12deg,#6d0c85 12deg 24deg)',transform:`rotate(${p*12}deg)`}}/>
    <div style={{position:'absolute',left:-400,right:-400,bottom:-70,height:compact?210:600,backgroundImage:'linear-gradient(#32e9f766 2px,transparent 2px),linear-gradient(90deg,#32e9f766 2px,transparent 2px)',backgroundSize:'85px 85px',transform:'perspective(500px) rotateX(58deg)',transformOrigin:'bottom',borderTop:'5px solid #ec42a0',boxShadow:'0 -5px 30px #ff4ec7'}}/>
    <div style={{position:'absolute',top:compact?25:130,left:50,fontFamily:mono,fontSize:compact?21:30,lineHeight:1.45,textShadow:'2px 1px #f0f, -2px -1px #0ff'}}>PLAY ▶<br/><span style={{fontSize:compact?17:21}}>НОВАЯ ЭРА · ДЕМО</span></div>
    <div style={{position:'absolute',top:compact?30:140,right:50,fontFamily:mono,fontSize:compact?20:30}}>00:{String(Math.floor(f/fps)).padStart(2,'0')}:{String(f%Math.round(fps)).padStart(2,'0')}</div>
    <div style={{position:'absolute',left:70,right:70,top:compact?75:300,fontSize:compact?58:92,textAlign:'center',lineHeight:1.0,color:'#ffd52e',textShadow:'4px 6px 0 #e0385e',transform:`scale(${appear(f,0,fps)})`}}>{c.title.toUpperCase()}</div>
    <div style={{position:'absolute',left:240,top:bodyY,width:600,height:800,transform:`translateY(${(1-a)*500}px) scale(${a*zoom*unitScale}) rotate(${Math.sin(p*Math.PI*3)*2}deg)`,transformOrigin:'top center'}}>
      <div style={{position:'absolute',left:247,top:-75,width:100,height:100,border:'13px solid #e0e6df',borderRadius:'50%'}}/>
      <div style={{position:'absolute',inset:0,background:'radial-gradient(circle at 30% 20%,#8df3dd,#21cfc9 43%,#079da9 85%)',borderRadius:'47% 47% 43% 43% / 53% 53% 40% 40%',boxShadow:'inset -20px -20px 40px #00575b88, inset 15px 20px 20px #c2ffed88, 16px 25px 20px #16012788'}}/>
      {Array.from({length:16},(_,i)=><div key={i} style={{position:'absolute',left:35+noise(i)*510,top:40+noise(i+100)*690,width:10+noise(i+50)*13,height:10+noise(i+50)*13,borderRadius:'50%',background:['#eb70b3','#ffe64d','#fff','#3a7eaf'][i%4],opacity:.6}}/>)}
      <div style={{position:'absolute',left:115,top:215,width:370,height:310,background:'#29215b',borderRadius:45,padding:25,boxSizing:'border-box',boxShadow:'inset 7px 6px 0 #131a3d'}}>
        <div style={{position:'relative',width:'100%',height:'100%',background:'linear-gradient(#a8b57b,#8f9d61)',overflow:'hidden'}}>
          <div style={{position:'absolute',left:15,top:12,fontFamily:mono,fontSize:25,color:'#24392a'}}>{p<.5?'ЗАДАЧА':'ГОТОВО'}</div>
          <svg style={{position:'absolute',left:80,top:75,width:170,height:150}} viewBox="0 0 17 15" shapeRendering="crispEdges"><path d="M4 2 H13 V4 H15 V11 H13 V13 H4 V11 H2 V4 H4 Z" fill="#263a28"/>{eyeBlink?<path d="M5 6 H7 M10 6 H12" stroke="#a5b278"/>:<><rect x="5" y="5" width="2" height="2" fill="#a5b278"/><rect x="10" y="5" width="2" height="2" fill="#a5b278"/></>}<path d={p>.5?'M5 9 H7 V10 H10 V9 H12 V11 H5 Z':'M7 9 H10 V10 H7 Z'} fill="#a5b278"/></svg>
          <div style={{position:'absolute',inset:0,background:'repeating-linear-gradient(0deg,transparent 0px,transparent 3px,#14271a22 4px)'}}/>
        </div>
      </div>
      {[0,1,2].map(i=><div key={i} style={{position:'absolute',left:165+i*108,top:620,width:68,height:68,borderRadius:'50%',background:'radial-gradient(circle at 30% 25%,#ffaad5,#d81986 45%,#6d1259)',boxShadow:'3px 6px 0 #0b657a',transform:`translateY(${i===1&&p>.35&&p<.41?9:0}px)`}}/>)}
      <div style={{position:'absolute',left:0,right:0,bottom:40,textAlign:'center',fontFamily:mono,color:'#08576b',fontSize:20}}>VIRTUAL ASSISTANT · DEMO</div>
    </div>
    <div style={{position:'absolute',left:65,top:compact?245:820,padding:'13px 24px',fontSize:compact?26:43,background:'#fff8b0',color:'#28145b',border:'5px solid #bc257e',transform:`rotate(-7deg) scale(${appear(f,span*.27,fps)})`,boxShadow:'7px 7px 0 #140b38'}}>{c.labels[0]}</div>
    <div style={{position:'absolute',right:70,top:compact?195:615,transform:`rotate(8deg) scale(${appear(f,span*.42,fps)})`}}><Star size={compact?130:210} color="#ffd729"/><div style={{position:'absolute',inset:0,display:'flex',alignItems:'center',justifyContent:'center',color:'#a92057',fontSize:compact?24:38}}>НОВОЕ!</div></div>
    {[0,1,2].map(i=>{const phase=(p*2+i*.37)%1;return <div key={i} style={{position:'absolute',left:[170,875,110][i],top:compact?[140,350,430][i]:[530,1000,1350][i],fontSize:compact?40:70,color:'#fff9ab',opacity:Math.sin(phase*Math.PI),transform:`scale(${.4+Math.sin(phase*Math.PI)*.6})`}}>✦</div>})}
    <div style={{position:'absolute',bottom:compact?35:200,left:90,right:90,textAlign:'center',fontSize:compact?37:65,color:'#fff1b8',background:'#b5167c',padding:'12px 20px',border:'5px solid #ffe438',boxShadow:'8px 9px 0 #180d3e',transform:`scale(${appear(f,span*.58,fps)})`}}>{p<.65?c.labels[1]:`${c.labels[2]}: ${count}%`}</div>
    <AbsoluteFill style={{background:'repeating-linear-gradient(0deg,transparent 0px,transparent 3px,#08001630 4px)',pointerEvents:'none',mixBlendMode:'multiply'}}/>
    <div style={{position:'absolute',top:`${((f*3)%110)}%`,left:0,right:0,height:10,background:'#fff',opacity:Math.floor(f/4)%17===0?.22:0}}/>
    <AbsoluteFill style={{boxShadow:'inset 0 0 200px 70px #0008',pointerEvents:'none'}}/>
  </AbsoluteFill>;
};
