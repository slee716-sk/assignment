'use strict';
const ROAD_COLORS=['#f1e8f4','#d9bde1','#b98bc8','#925aa7','#673681'];
const roadSmall=r=>r.n<30||r.road_limited_n<30;
function roadNode(tag,attrs={},text){
  const el=document.createElementNS(NS,tag);
  Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,String(v)));
  if(text!==undefined)el.textContent=text;
  return el;
}
function roadSelect(el,name){
  el.dataset.name=name;el.setAttribute('tabindex','0');el.setAttribute('role','button');
  el.addEventListener('click',()=>choose(name));
  el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();choose(name)}});
}
function renderRoadMap(){
  const g=$('road-map-shapes');g.replaceChildren();
  rows.forEach(r=>{
    const small=r.road_limited_n<30,none=r.road_limited_pct==null;
    const path=roadNode('path',{d:r.path,'fill-rule':'evenodd',
      fill:small?'url(#road-small)':ROAD_COLORS[Math.min(Math.floor(r.road_limited_pct/20),4)],
      class:'road-district','aria-label':`${r.name}, 접도 제약 ${fmt(r.road_limited_pct,1)}%, 제약 ${r.road_limited_count}채, 유효 ${r.road_limited_n}채${small?', 유효 표본 30채 미만':''}`});
    path.append(roadNode('title',{},`${r.name} · 접도 제약 ${none?'자료 없음':fmt(r.road_limited_pct,1)+'%'} (${r.road_limited_count}/${r.road_limited_n}채)`));
    roadSelect(path,r.name);g.append(path);
  });
  rows.forEach(r=>{
    const t=roadNode('text',{x:r.label_xy[0],y:r.label_xy[1],
      fill:r.road_limited_n>=30&&r.road_limited_pct>=60?'#fff':'#183344',class:'district-label'},r.name);
    t.append(roadNode('tspan',{x:r.label_xy[0],dy:15},r.road_limited_pct==null?'자료 없음':fmt(r.road_limited_pct,1)+'%'));g.append(t);
  });
}
function renderRoadDetail(){
  const r=rows.find(x=>x.name===selected),m=metric(r);
  const omitted=roadSmall(r)&&!$('scatter-small-toggle').checked;
  $('road-detail').innerHTML=`<div><span class="eyebrow">선택한 자치구</span><strong>${r.name}</strong></div><div><span>접도 제약 빈집 비율</span><strong>${fmt(r.road_limited_pct,1)}%</strong><small>제약 ${fmt(r.road_limited_count,0)} / 유효 ${fmt(r.road_limited_n,0)}채 · 미확인 ${fmt(r.road_unknown_n,0)}채</small></div><div><span>${period==='18'?'첫 18개월':'전체기간'} 해소신호 발생률</span><strong>${fmt(m.rate)}<small>건 / 100호·년</small></strong><small>95% 신뢰구간 ${fmt(m.lo)}–${fmt(m.hi)}건</small></div><p>${omitted?'현재 산점도에는 소표본으로 제외되어 있다. 위 체크박스로 표시할 수 있다.':'지도·산점도·앞의 비교 그래프에서 선택한 구가 함께 강조된다.'}</p>`;
}
function renderRoadScatter(){
  const svg=$('road-scatter'),include=$('scatter-small-toggle').checked;
  const points=rows.filter(r=>r.road_limited_pct!=null&&(include||!roadSmall(r)));
  const left=72,right=616,top=24,bottom=384;
  const max=Math.max(5,Math.ceil(Math.max(...points.map(r=>metric(r).hi))/5)*5);
  const x=v=>left+(right-left)*v/100,y=v=>bottom-(bottom-top)*v/max;
  svg.replaceChildren();
  svg.append(roadNode('title',{},`접도 제약과 ${period==='18'?'첫 18개월':'전체기간'} 발생률, ${points.length}개 구`));
  for(let i=0;i<=5;i++){
    const xv=i*20,yv=max*i/5;
    svg.append(roadNode('line',{x1:x(xv),x2:x(xv),y1:top,y2:bottom,class:'scatter-grid'}));
    svg.append(roadNode('line',{x1:left,x2:right,y1:y(yv),y2:y(yv),class:'scatter-grid'}));
    svg.append(roadNode('text',{x:x(xv),y:bottom+23,'text-anchor':'middle',class:'scatter-tick'},fmt(xv,0)));
    svg.append(roadNode('text',{x:left-12,y:y(yv)+4,'text-anchor':'end',class:'scatter-tick'},fmt(yv,max>=10?0:1)));
  }
  svg.append(roadNode('line',{x1:x(D.total.road_limited_pct),x2:x(D.total.road_limited_pct),y1:top,y2:bottom,class:'scatter-road-ref'}));
  svg.append(roadNode('line',{x1:left,x2:right,y1:y(metric(D.total).rate),y2:y(metric(D.total).rate),class:'scatter-rate-ref'}));
  svg.append(roadNode('text',{x:(left+right)/2,y:bottom+57,'text-anchor':'middle',class:'scatter-axis-label'},'접도 제약 빈집 비율 (%)'));
  svg.append(roadNode('text',{transform:`translate(19 ${(top+bottom)/2}) rotate(-90)`,'text-anchor':'middle',class:'scatter-axis-label'},'해소신호 발생률 (100호·년당 건수)'));
  points.forEach(r=>{
    const m=metric(r),cx=x(r.road_limited_pct),cy=y(m.rate);
    const g=roadNode('g',{class:`scatter-point${roadSmall(r)?' small-point':''}`,'aria-label':`${r.name}, 접도 제약 ${fmt(r.road_limited_pct,1)}%, 발생률 ${fmt(m.rate)}, 95% 신뢰구간 ${fmt(m.lo)}에서 ${fmt(m.hi)}, 표본 ${r.n}채`});
    g.append(roadNode('title',{},`${r.name} · 접도 ${fmt(r.road_limited_pct,1)}% · 신호 ${fmt(m.rate)}건 · 유효 ${r.road_limited_n}채`));
    g.append(roadNode('line',{x1:cx,x2:cx,y1:y(m.hi),y2:y(m.lo),class:'scatter-ci'}));
    g.append(roadNode('circle',{cx,cy,r:15,class:'scatter-hit'}));
    g.append(roadNode('circle',{cx,cy,r:6,class:'scatter-marker'}));
    g.append(roadNode('text',{x:cx+(r.road_limited_pct>75?-11:11),y:cy-11,
      'text-anchor':r.road_limited_pct>75?'end':'start',class:'scatter-label'},r.name));
    roadSelect(g,r.name);svg.append(g);
  });
  const stats=D.road_relationship[include?'all':'main'][period];
  $('scatter-note').textContent=`${points.length}개 구 · 스피어만 순위상관 ${fmt(stats.rho)} · ${period==='18'?'판정 후 첫 18개월':'전체 관찰기간'}. 인과관계를 뜻하지 않는다.`;
  choose(selected);
}
$('relation-period').addEventListener('change',e=>setPeriod(e.target.value));
$('scatter-small-toggle').addEventListener('change',renderRoadScatter);
renderRoadMap();renderRoadScatter();
