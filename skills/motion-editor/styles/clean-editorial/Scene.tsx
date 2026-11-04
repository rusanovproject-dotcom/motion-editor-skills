import React from 'react';
import {AbsoluteFill, useVideoConfig} from 'remotion';
import {StyleSceneProps, sans, mono, mix, smooth, appear, Star, Check} from '../../assets/scene-kit/shared';

export const StyleScene: React.FC<StyleSceneProps> = ({c,f,span,compact}) => {
  const {fps}=useVideoConfig();
  const orbitId = React.useId().replace(/:/g, "");
  const p=f/span; const reveal=appear(f,5,fps);
  const wipe=smooth((p-.43)/.13); const dark=p>.52;
  const cardToProduct=smooth((p-.18)/.18);
  const title=c.title||'Идея становится продуктом';
  const headY=compact?55:230, objectY=compact?250:720;
  const titleOffset=(1-reveal)*50;
  const diskCenterY=compact?470:1320;
  const diskRadius=950*1.55*wipe;
  const headingMask=`circle(${diskRadius}px at ${540-80}px ${diskCenterY-headY-titleOffset}px)`;
  const titleWords=title.split(' ');
  const headingText=()=>titleWords.map((w,i)=><React.Fragment key={i}><span style={{color:i===titleWords.length-1?c.accent:undefined}}>{w}</span>{' '}</React.Fragment>);
  const labels=c.labels.length>=3?c.labels:['Идея','Продукт','Готово'];
  return <AbsoluteFill style={{background:'#f4f4ef',color:'#111',fontFamily:sans,overflow:'hidden'}}>
    <div style={{position:'absolute',left:-80,top:compact?20:70,transform:`rotate(${p*28}deg)`}}><Star size={200}/></div>
    <div style={{position:'absolute',right:-75,bottom:-55,transform:`rotate(${-p*35}deg)`}}><Star size={300}/></div>
    <div style={{position:'absolute',left:80,top:headY,width:920,opacity:reveal,transform:`translateY(${titleOffset}px)`,fontSize:compact?57:86,lineHeight:1.08,fontWeight:400,letterSpacing:-4,zIndex:4,color:'#111'}}>
      {headingText()}
      <div aria-hidden="true" style={{position:'absolute',inset:0,color:'#f4f4ef',clipPath:headingMask}}>{headingText()}</div>
    </div>
    <div style={{position:'absolute',left:86,top:headY+(compact?130:220),fontFamily:mono,fontSize:compact?18:24,color:dark?'#aaa':'#777',zIndex:4}}>{c.subtitle}</div>
    <div style={{position:'absolute',left:250,top:objectY,width:580,height:compact?260:430,background:'#fff',border:'2px solid #111',borderRadius:mix(cardToProduct,2,32),boxShadow:'15px 22px 40px #00000018',opacity:p<.48?reveal:1-wipe,transform:`translateY(${(1-reveal)*170}px) rotate(${mix(cardToProduct,-5,0)}deg) scale(${mix(cardToProduct,.93,1)})`,padding:40,boxSizing:'border-box'}}>
      <div style={{display:'flex',gap:14,marginBottom:30}}>{[0,1,2].map(i=><div key={i} style={{width:16,height:16,borderRadius:20,background:i===0?c.accent:'#ddd'}}/>)}</div>
      <div style={{fontSize:compact?42:58,letterSpacing:-2,marginBottom:24}}>{cardToProduct<.5?labels[0]:labels[1]}</div>
      {[0,1,2].map(i=><div key={i} style={{height:compact?13:20,width:`${85-i*17}%`,background:i===0?c.accent:'#e9e9e4',marginTop:18,borderRadius:8,transformOrigin:'left',transform:`scaleX(${smooth((p-.18-i*.035)/.16)})`}}/>)}
      <div style={{position:'absolute',right:-40,bottom:-35,transform:`scale(${appear(f,span*.30,fps)})`}}><Check color={c.accent}/></div>
    </div>
    <div style={{position:'absolute',left:540,top:diskCenterY,width:1900,height:1900,borderRadius:'50%',background:'#101010',transform:`translate(-50%,-50%) scale(${wipe*1.55})`,transformOrigin:'center'}}/>
    {p>.48&&<>
      <div style={{position:'absolute',left:390,top:objectY+(compact?10:35),width:300,height:300,borderRadius:'50%',background:`radial-gradient(circle at 30% 25%, #fff 0%, #697383 12%, #202a3b 40%, #0b1020 68%, ${c.accent} 100%)`,boxShadow:'inset -12px -20px 35px #4263eb50',transform:`scale(${appear(f,span*.55,fps)})`}}/>
      <svg style={{position:'absolute',left:280,top:objectY-110,width:520,height:520,transform:`rotate(${(p-.5)*65}deg)`}} viewBox="0 0 520 520"><defs><path id={orbitId} d="M260 260 m-225 0 a225 225 0 1 1 450 0 a225 225 0 1 1 -450 0"/></defs><text fill="#fff" fontSize="19" fontFamily={mono} letterSpacing="5"><textPath href={`#${orbitId}`}>ИДЕЯ · ПРОДУКТ · РЕЗУЛЬТАТ · ИДЕЯ · ПРОДУКТ · РЕЗУЛЬТАТ · </textPath></text></svg>
      {!compact&&[0,1,2].map(i=>{const a=appear(f,span*(.67+i*.055),fps);return <div key={i} style={{position:'absolute',left:110+i*300,top:1390+(i%2)*100,width:260,padding:'25px 12px',background:'#f4f4ef',borderRadius:50,color:'#151515',fontSize:28,textAlign:'center',transform:`translateY(${(1-a)*100}px) scale(${a})`}}>{labels[i]}</div>})}
      <div style={{position:'absolute',left:80,right:80,bottom:compact?25:150,fontSize:compact?38:65,color:'#fff',letterSpacing:-2,opacity:smooth((p-.7)/.1),textAlign:'center'}}>{labels[2]}<span style={{color:c.accent}}> — это только начало.</span></div>
    </>}
  </AbsoluteFill>;
}

