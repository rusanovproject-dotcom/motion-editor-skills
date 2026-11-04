import React from "react";
import {AbsoluteFill, Img, useVideoConfig} from "remotion";
import {SceneConfig, StyleSceneProps, mono, condensed, mix, smooth, appear, localAsset, Grain} from "../../assets/scene-kit/shared";

const PaperCard:React.FC<{label:string;index:number;progress:number;image?:string}>=({label,index,progress,image})=><div style={{width:230,height:290,padding:15,background:'#eee8d5',boxShadow:'5px 12px 13px #0007',transform:`translateY(${(1-progress)*130}px) rotate(${mix(progress,10,index%2?3:-3)}deg) scale(${progress})`,transformOrigin:'center'}}>
  <div style={{background:'#193036',height:220,display:'flex',alignItems:'center',justifyContent:'center',overflow:'hidden'}}>{image?<Img src={localAsset(image)} style={{width:'90%',height:'90%',objectFit:'contain',filter:'drop-shadow(3px 3px 0 #fff) drop-shadow(-3px -3px 0 #fff)'}}/>:<svg width="170" height="170" viewBox="0 0 170 170"><rect x="30" y="20" width="110" height="125" rx="12" fill="#ece7d8" stroke="#fff" strokeWidth="6"/><rect x="45" y="40" width="80" height="55" rx="5" fill="#29454c"/><path d="M57 110 H112 M57 124 H99" stroke="#b5a782" strokeWidth="7"/><circle cx="105" cy="65" r="12" fill="#d54832"/></svg>}</div>
  <div style={{fontFamily:mono,fontSize:22,textAlign:'center',color:'#151515',marginTop:18}}>{label}</div>
</div>;

function Collage({c,f,span,compact}:{c:SceneConfig;f:number;span:number;compact:boolean}) {
  const {fps}=useVideoConfig();const p=f/span;
  const move=smooth((p-.7)/.23); const title=c.title.toUpperCase();
  return <AbsoluteFill style={{background:'radial-gradient(ellipse at 45% 45%,#294248,#14282c 75%)',overflow:'hidden',color:'#f0ead8'}}>
    <Grain/>
    <div style={{position:'absolute',left:70,top:compact?35:130,right:70,fontFamily:condensed,fontSize:compact?60:104,letterSpacing:1,lineHeight:1.0,transform:`translateY(${(1-appear(f,0,fps))*100}px)`}}>{title}</div>
    <div style={{position:'absolute',left:100,top:compact?135:410,width:880,height:compact?320:800,transform:`rotate(-3deg) translateY(${(1-appear(f,8,fps))*80}px)`,background:'#e7dfc8',boxShadow:'8px 15px 20px #0006'}}>
      <svg width="100%" height="100%" viewBox="0 0 880 800" preserveAspectRatio="none"><rect width="880" height="800" fill="#ddd5bd"/>{Array.from({length:18},(_,i)=><path key={i} d={`M${i*70-250} 0 L${i*70+300} 800 M0 ${i*60} L880 ${i*60-200}`} stroke="#b7af97" fill="none" strokeWidth={i%4===0?8:3}/>)}<path d="M0 200 C300 600 400 100 880 600" stroke="#98b1b6" strokeWidth="70" fill="none"/></svg>
      <div style={{position:'absolute',left:'53%',top:'40%',width:45,height:45,borderRadius:50,background:'#cf4432',boxShadow:'6px 8px 7px #0003',transform:`scale(${appear(f,span*.15,fps)})`}}/>
    </div>
    <div style={{position:'absolute',left:60,top:compact?215:600,padding:compact?'12px 25px':'20px 35px',background:'#f0ead8',color:'#121c20',fontFamily:condensed,fontSize:compact?52:92,transform:`rotate(-5deg) translateX(${(1-appear(f,span*.15,fps))*-650}px)`}}>{c.labels[0]}</div>
    <div style={{position:'absolute',right:85,top:compact?320:810,padding:'12px 30px',border:'8px solid #b7382e',color:'#b7382e',fontFamily:condensed,fontSize:compact?40:70,background:'#efe8d7',transform:`rotate(9deg) scale(${appear(f,span*.29,fps)})`}}>{c.labels[1]}</div>
    <div style={{position:'absolute',left:0,right:0,bottom:0,height:compact?175:520,background:'#b8302b',transform:`translateY(${(1-smooth((p-.43)/.14))*650}px)`}}/>
    <div style={{position:'absolute',left:100,top:compact?390:1050,width:880,display:'grid',gridTemplateColumns:'repeat(3,230px)',gap:35,transform:`translate(${move*-100}px,${move*-260}px) scale(${1+move*.35})`,transformOrigin:'center'}}>{Array.from({length:compact?3:6},(_,i)=><PaperCard key={i} label={c.labels[i%3]} index={i} image={c.images?.[i%c.images.length]} progress={appear(f,span*(.43+i*.045),fps)}/>)}</div>
    <div style={{position:'absolute',left:70,right:70,bottom:compact?20:105,background:'#efe8d7',color:'#16272b',fontFamily:condensed,fontSize:compact?45:74,padding:'15px 30px',textAlign:'center',transform:`rotate(-3deg) scale(${appear(f,span*.79,fps)})`,boxShadow:'7px 10px 0 #0004'}}>{c.labels[2]}</div>
  </AbsoluteFill>;
}


export const StyleScene: React.FC<StyleSceneProps> = Collage;
