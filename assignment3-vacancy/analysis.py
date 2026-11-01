"""Reproduce Assignment 3 from frozen local extracts; never edits research inputs."""
from pathlib import Path
import sys, json, hashlib, io, math, os
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.deps'))
import pandas as pd
import numpy as np
from scipy.stats import chi2, spearmanr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Patch
from shapely.geometry import shape

PROJECT = Path(os.environ.get('VACANCY_RESEARCH_ROOT', ROOT)).resolve()
PRIVATE = ROOT / 'private'
DIST = ROOT / 'public'
END = pd.Timestamp('2026-04-30')
INPUT_MANIFEST = json.loads((ROOT/'input_manifest.json').read_text(encoding='utf-8'))
COLS = ['vid','시도','시군구','pnu','주택유형','판정일','추적시작','해소','해소일',
        '집합','분석대상','결과_대분류','보류사유','제외사유','판정일_근거','대상_주용도',
        '판정일_마지막취득','법인','건축연령','해소_첫신호','해소_확실','해소일_확실','명부전신호']
COLORS = ['#e7f0f5','#bdD6e6','#83b3d0','#4485ad','#205476']

def exposure(start, signal, signal_date, end):
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    hit = pd.to_datetime(signal_date, errors='coerce')
    if pd.isna(start) or pd.isna(end) or start >= end:
        raise ValueError('Missing or non-positive observation interval')
    if signal and pd.isna(hit):
        raise ValueError('Signal without a date')
    if signal and hit < start:
        raise ValueError('Signal precedes baseline')
    observed = bool(signal and hit <= end)
    stop = hit if observed else end
    years = (stop-start).total_seconds() / (365.25*86400)
    if years <= 0:
        raise ValueError('Zero or negative exposure; cannot silently add time')
    return int(observed), years

def rate_ci(events, years):
    if years <= 0:
        return None, None, None
    lo = 0 if events == 0 else chi2.ppf(.025, 2*events)/2
    hi = chi2.ppf(.975, 2*events+2)/2
    return events / years * 100, float(lo/years*100), float(hi/years*100)

def road_flag(value):
    limited={'맹지','세로(불)','세로한면(불)','세로각지(불)','세각(불)'}
    other={'세로(가)','세로한면(가)','세로각지(가)','세각(가)','소로한면','소로각지',
           '중로한면','중로각지','광대한면','광대로한면','광대소각','광대세각'}
    if value in limited: return 1
    if value in other: return 0
    return None

def road_summary(values):
    known = pd.Series(values, dtype=float).dropna()
    count, n = int(known.sum()), len(known)
    return count, n, None if n == 0 else count / n * 100

def snap(source, name, columns=None, seoul=False):
    target = PRIVATE/name
    if target.exists():
        assert hashlib.sha256(target.read_bytes()).hexdigest() == INPUT_MANIFEST[name]['snapshot_sha256'], 'Frozen input hash differs'
        return pd.read_csv(target,dtype=str).fillna('')
    raw = source.read_bytes()
    h = hashlib.sha256(raw).hexdigest()
    assert h == INPUT_MANIFEST[name]['source_sha256'], 'Source differs from the publication snapshot; do not overwrite the published cohort'
    d = pd.read_csv(io.BytesIO(raw),dtype=str,usecols=columns).fillna('')
    if seoul:
        d = d[d['시도'].str.startswith('서울')].copy()
    assert hashlib.sha256(source.read_bytes()).hexdigest() == h, 'Source changed during snapshot'
    d.to_csv(target,index=False,encoding='utf-8-sig')
    meta = {'source':str(source.relative_to(PROJECT)), 'source_sha256':h,
            'source_mtime':source.stat().st_mtime,'snapshot_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'rows':len(d),'columns':list(d.columns)}
    target.with_suffix('.metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    return d

def color(r):
    if r['n'] < 30: return '#d4d9dd'
    return COLORS[min(int(r['rate']//3),4)]

def aggregate(d, name):
    k, y = int(d.event.sum()),float(d.years.sum())
    rate,lo,hi=rate_ci(k,y)
    r18,l18,h18=rate_ci(int(d.event18.sum()),float(d.years18.sum()))
    out = {'name':name,'n':len(d),'events':k,'years':y,'rate':rate,'lo':lo,'hi':hi,
           'median_years':float(d.years.median()),'baseline_min':str(d['판정일'].min().date()),
           'baseline_max':str(d['판정일'].max().date()),'small_sample':bool(len(d)<30),
           'events18':int(d.event18.sum()),'years18':float(d.years18.sum()),
           'rate18':r18,'lo18':l18,'hi18':h18,
           'certain_events':int(d.event_certain.sum()),'certain_years':float(d.years_certain.sum()),
           'certain_rate':rate_ci(int(d.event_certain.sum()),float(d.years_certain.sum()))[0]}
    for col in ['long_held','road_limited','commercial','old_building']:
        known=d[col].dropna()
        out[col+'_n']=len(known)
        out[col+'_pct']=None if len(known)==0 else float(known.mean()*100)
    count, known, pct = road_summary(d.road_limited)
    out.update(road_limited_count=count, road_limited_n=known,
               road_limited_pct=pct, road_unknown_n=len(d)-known)
    out['land_price_n']=int(d.land_price.notna().sum())
    out['land_price_median']=None if d.land_price.notna().sum()==0 else float(d.land_price.median())
    out['future_land_n']=int(d.land_year.gt(d['판정일'].dt.year).sum())
    return out

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    PRIVATE.mkdir(exist_ok=True); (DIST/'assets').mkdir(parents=True,exist_ok=True)
    s=snap(PROJECT/'work/national/전국빈집_집별_v2.csv','seoul_minimal.csv',COLS,True)
    a=s[(s['분석대상']=='True')&(s['집합']=='False')].copy()
    assert not a.vid.duplicated().any()
    assert (a['판정일']==a['추적시작']).all()
    for c in ['판정일','해소일','해소일_확실','판정일_마지막취득']:
        if c in a: a[c]=pd.to_datetime(a[c],errors='coerce')
    a[['event','years']]=[exposure(r['판정일'],r['해소']=='True',r['해소일'],END) for _,r in a.iterrows()]
    a[['event_certain','years_certain']]=[exposure(r['판정일'],r['해소_확실']=='True',r['해소일_확실'],END) for _,r in a.iterrows()]
    assert (a['판정일']+pd.DateOffset(months=18)<=END).all(), '18-month horizon unavailable'
    a[['event18','years18']]=[exposure(r['판정일'],r['해소']=='True',r['해소일'],r['판정일']+pd.DateOffset(months=18)) for _,r in a.iterrows()]
    acq=a['판정일_마지막취득']
    a['long_held']=(a['판정일']>=acq+pd.DateOffset(years=20)).astype(float).where(acq.notna())
    age=pd.to_numeric(a['건축연령'],errors='coerce'); a['old_building']=age.ge(40).astype(float).where(age.notna())
    lc=snap(PROJECT/'공개자료/08_토지특성/서울_토지특성_api.csv','seoul_land.csv',
            ['조회pnu','상태','stdrYear','prposArea1Nm','roadSideCodeNm','pblntfPclnd'])
    lc=lc[lc['상태']=='ok'].copy(); lc['land_year']=pd.to_numeric(lc.stdrYear,errors='coerce')
    join=a[['vid','pnu','판정일']].merge(lc,left_on='pnu',right_on='조회pnu',how='left')
    join['dist']=(join.land_year-join['판정일'].dt.year).abs()+(join.land_year>join['판정일'].dt.year)*.5
    join=join.sort_values(['vid','dist','land_year']).drop_duplicates('vid').set_index('vid')
    road=a.vid.map(join.roadSideCodeNm).fillna(''); zone=a.vid.map(join.prposArea1Nm).fillna('')
    a['road_limited']=pd.to_numeric(road.map(road_flag),errors='coerce')
    a['commercial']=zone.str.contains('상업|준주거',regex=True).astype(float).where(zone.ne('')&~zone.str.contains('지정되지'))
    a['land_price']=pd.to_numeric(a.vid.map(join.pblntfPclnd),errors='coerce').where(lambda x:x>0)
    a['land_year']=a.vid.map(join.land_year)
    rows=[aggregate(d,n) for n,d in a.groupby('시군구')]
    total=aggregate(a,'서울 전체')
    boundary=json.loads((ROOT/'data'/'seoul_boundary_2015.geojson').read_text(encoding='utf-8-sig'))
    assert len(boundary['features'])==25
    assert {f['properties']['SIG_KOR_NM'] for f in boundary['features']}=={r['name'] for r in rows}
    geometries={f['properties']['SIG_KOR_NM']:shape(f['geometry']) for f in boundary['features']}
    cos=math.cos(math.radians(37.55)); points=[]
    for g in geometries.values():
        geoms=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
        for p in geoms: points.extend(list(p.exterior.coords))
    xmin,xmax=min(p[0]*cos for p in points),max(p[0]*cos for p in points)
    ymin,ymax=min(p[1] for p in points),max(p[1] for p in points)
    scale=min(820/(xmax-xmin),600/(ymax-ymin))
    def project(x,y): return 30+(x*cos-xmin)*scale,30+(ymax-y)*scale
    for r in rows:
        g=geometries[r['name']]; polys=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
        parts=[]
        for p in polys:
            for ring in [p.exterior]+list(p.interiors):
                xy=[project(x,y) for x,y in ring.coords]
                parts.append('M'+'L'.join(f'{x:.2f},{y:.2f}' for x,y in xy)+'Z')
        r['path']=''.join(parts); pt=g.representative_point(); r['label_xy']=list(project(pt.x,pt.y))
        r['color']=color(r)
    rows.sort(key=lambda r:r['rate'])
    mainrows=[r for r in rows if not r['small_sample']]
    cor={}
    for c in ['long_held_pct','road_limited_pct','commercial_pct','land_price_median','old_building_pct']:
        valid=[r for r in mainrows if r[c] is not None]
        coef,p=spearmanr([r['rate'] for r in valid],[r[c] for r in valid])
        cor[c]={'rho':float(coef),'n':len(valid)}
    relationship={}
    for scope in ['main','all']:
        valid=[r for r in rows if r['road_limited_n']>0 and
               (scope=='all' or (r['n']>=30 and r['road_limited_n']>=30))]
        relationship[scope]={key:{'rho':float(spearmanr(
            [r['road_limited_pct'] for r in valid], [r[column] for r in valid]).statistic),
            'n':len(valid)} for key,column in [('full','rate'),('18','rate18')]}
    flow=pd.crosstab(s['결과_대분류'],s['집합']).to_dict()
    provenance=INPUT_MANIFEST['seoul_minimal.csv']
    summary={'total':total,'districts':rows,'flow':flow,'main_n_districts':len(mainrows),
             'end':'2026-04-30','baseline_min':total['baseline_min'],'baseline_max':total['baseline_max'],
             'sample_label':'단독·다가구 중심 비집합 빈집','source_sha256':provenance['source_sha256'],
             'correlations':cor,'road_relationship':relationship,
             'signal_types':a.loc[a.event==1,'해소_첫신호'].value_counts().to_dict(),
             'house_types':a['주택유형'].value_counts().to_dict(),'ledger_uses':a['대상_주용도'].value_counts().to_dict(),
             'boundary_source':'https://github.com/southkorea/seoul-maps/tree/master/juso/2015',
             'boundary_year':2015,'map_viewbox':[0,0,880,660]}
    (DIST/'data.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    (DIST/'data.js').write_text('window.REPORT_DATA='+json.dumps(summary,ensure_ascii=False,allow_nan=False)+';',encoding='utf-8')
    table=pd.DataFrame([{k:v for k,v in r.items() if k not in ['path','label_xy','color']} for r in rows])
    table.to_csv(DIST/'seoul_district_rates.csv',index=False,encoding='utf-8-sig')
    # Standalone scientific figures, exported as PNG and SVG.
    plt.rcParams.update({'font.family':'Malgun Gothic','axes.unicode_minus':False,'font.size':10,'svg.fonttype':'none'})
    fig,ax=plt.subplots(figsize=(10,8),layout='constrained')
    for r in rows:
        geom=geometries[r['name']]; polys=list(geom.geoms) if geom.geom_type=='MultiPolygon' else [geom]
        for p in polys:
            xy=np.asarray(p.exterior.coords); xy[:,0]*=cos
            ax.add_patch(Polygon(xy,closed=True,facecolor=r['color'],edgecolor='white',linewidth=1,
                                 hatch='///' if r['small_sample'] else None))
        pt=geom.representative_point(); ax.text(pt.x*cos,pt.y,r['name']+'\n'+f"{r['rate']:.1f}",ha='center',va='center',fontsize=8,
                                              color='white' if not r['small_sample'] and r['rate']>=9 else '#173347')
    ax.set_xlim(xmin-.015,xmax+.015);ax.set_ylim(ymin-.015,ymax+.015);ax.set_aspect('equal');ax.axis('off')
    ax.set_title('서울 자치구별 빈집 해소신호 발생률',loc='left',fontsize=17,pad=20)
    labels=['0–3 미만','3–6 미만','6–9 미만','9–12 미만','12 이상']
    ax.legend(handles=[Patch(facecolor=c,label=l) for c,l in zip(COLORS,labels)]+[Patch(facecolor='#d4d9dd',hatch='///',label='표본 30채 미만')],
              loc='lower center',bbox_to_anchor=(.5,-.06),ncol=3,frameon=False,title='100호·년당 건수 · 값이 높을수록 해소신호가 빈번')
    fig.text(.02,-.055,'판정일~2026-04-30 · 비집합 빈집 2,825채 · 경계: JUSO 2015 / southkorea/seoul-maps',fontsize=8,color='#526574')
    for ext in ['png','svg']:fig.savefig(DIST/f'assets/seoul_map.{ext}',dpi=180,bbox_inches='tight',facecolor='white')
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,9),layout='constrained')
    for i,r in enumerate(mainrows):
        ax.plot([r['lo'],r['hi']],[i,i],color='#7797ac',lw=1.5)
        ax.scatter(r['rate'],i,color='#1d668f',s=45,zorder=3)
        ax.text(max(x['hi'] for x in mainrows)*1.01,i,f"{r['rate']:.2f}   ({r['events']}/{r['n']})",va='center',fontsize=9)
    ax.set_yticks(range(len(mainrows)),[r['name'] for r in mainrows]);ax.invert_yaxis()
    ax.axvline(total['rate'],color='#d27b39',ls='--',label=f"서울 전체 {total['rate']:.2f}")
    ax.set_xlabel('해소신호 발생률 (100호·년당 건수)');ax.set_title('해소신호 발생률의 자치구별 차이',loc='left',fontsize=17,pad=18)
    ax.grid(axis='x',color='#e6edf1');ax.set_axisbelow(True);ax.spines[['top','right','left']].set_visible(False)
    ax.set_xlim(0,max(x['hi'] for x in mainrows)*1.36);ax.legend(frameon=False,loc='lower right')
    fig.text(.02,-.035,'점: 발생률 · 선: 포아송 95% 신뢰구간 · 괄호: 사건 수/표본 수 · 30채 이상인 20개 구. 작은 표본 5개 구는 별도 표에 제시.',fontsize=8)
    for ext in ['png','svg']:fig.savefig(DIST/f'assets/seoul_ranking.{ext}',dpi=180,bbox_inches='tight',facecolor='white')
    plt.close(fig)
    # Road share uses known road records only; unknown is never treated as unrestricted.
    road_colors=['#f1e8f4','#d9bde1','#b98bc8','#925aa7','#673681']
    fig,ax=plt.subplots(figsize=(10,8),layout='constrained')
    for r in rows:
        g=geometries[r['name']]; polys=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
        small=r['road_limited_n']<30
        col='#d4d9dd' if small else road_colors[min(int(r['road_limited_pct']//20),4)]
        for p in polys:
            xy=np.asarray(p.exterior.coords);xy[:,0]*=cos
            ax.add_patch(Polygon(xy,closed=True,facecolor=col,edgecolor='white',linewidth=1,
                                 hatch='///' if small else None))
        pt=g.representative_point()
        ax.text(pt.x*cos,pt.y,r['name']+'\n'+f"{r['road_limited_pct']:.1f}%",ha='center',va='center',fontsize=8,
                color='white' if not small and r['road_limited_pct']>=60 else '#173347')
    ax.set_xlim(xmin-.015,xmax+.015);ax.set_ylim(ymin-.015,ymax+.015);ax.set_aspect('equal');ax.axis('off')
    ax.set_title('서울 자치구별 접도 제약 빈집 비율',loc='left',fontsize=17,pad=20)
    ax.legend(handles=[Patch(facecolor=c,label=l) for c,l in zip(road_colors,
              ['0–20 미만','20–40 미만','40–60 미만','60–80 미만','80–100'])]+
              [Patch(facecolor='#d4d9dd',hatch='///',label='접도 유효 표본 30채 미만')],
              loc='lower center',bbox_to_anchor=(.5,-.06),ncol=3,frameon=False,title='유효 표본 중 맹지·차량통행 불가 비율 (%)')
    fig.text(.02,-.055,f"유효 {total['road_limited_n']:,}채 중 {total['road_limited_count']:,}채 · 서울 {total['road_limited_pct']:.1f}% · 경계: JUSO 2015 / southkorea/seoul-maps",fontsize=8,color='#526574')
    for ext in ['png','svg']:fig.savefig(DIST/f'assets/seoul_road_map.{ext}',dpi=180,bbox_inches='tight',facecolor='white')
    plt.close(fig)
    for period,rate,lo,hi,suffix,title in [
        ('full','rate','lo','hi','', '전체 관찰기간'),
        ('18','rate18','lo18','hi18','_18months','판정 후 첫 18개월')]:
        points=[r for r in mainrows if r['road_limited_n']>=30]
        fig,ax=plt.subplots(figsize=(10,7),layout='constrained')
        for r in points:
            ax.errorbar(r['road_limited_pct'],r[rate],yerr=[[r[rate]-r[lo]],[r[hi]-r[rate]]],
                        fmt='o',color='#216589',ecolor='#c4d5df',ms=7,capsize=2,zorder=3)
            if r['name'] in ['용산구','성동구','노원구','서초구','도봉구']:
                ax.annotate(r['name'],(r['road_limited_pct'],r[rate]),xytext=(7,5),textcoords='offset points',fontsize=10)
        ax.axvline(total['road_limited_pct'],color='#925aa7',ls='--',lw=1.2,
                   label=f"서울 접도 제약 {total['road_limited_pct']:.1f}%")
        ax.axhline(total[rate],color='#b9672b',ls='--',lw=1.2,label=f"서울 발생률 {total[rate]:.2f}건")
        ax.set_xlim(0,100);ax.set_ylim(0,math.ceil(max(r[hi] for r in points)/5)*5)
        ax.set_xlabel('접도 제약 빈집 비율 (%)');ax.set_ylabel('해소신호 발생률 (100호·년당 건수)')
        ax.set_title(f'접도 제약과 해소신호 · {title}',loc='left',fontsize=17,pad=20)
        ax.grid(color='#e6edf1');ax.set_axisbelow(True);ax.spines[['top','right']].set_visible(False)
        ax.legend(frameon=False,fontsize=9,loc='upper right')
        rho=relationship['main'][period]['rho']
        fig.text(.02,-.035,f'표본·접도 유효 표본 각 30채 이상 20개 구 · 세로선: 발생률 포아송 95% 신뢰구간 · 순위상관 {rho:.2f}\n구 단위의 기술적 관계이며 인과관계를 뜻하지 않음. 접도 조건은 판정 연도 인근 자료로 고정.',fontsize=8,color='#526574')
        for ext in ['png','svg']:fig.savefig(DIST/f'assets/seoul_road_scatter{suffix}.{ext}',dpi=180,bbox_inches='tight',facecolor='white')
        plt.close(fig)
    for svg in (DIST/'assets').glob('*.svg'):
        svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
    checks={'unique_vid':not a.vid.duplicated().any(),'baseline_equals_start':bool((a['판정일']==a['추적시작']).all()),
            'positive_exposure':bool((a.years>0).all()),'all_25_gu_mapped':len(rows)==25,
            'counts_reconcile':sum(r['n'] for r in rows)==total['n'] and sum(r['events'] for r in rows)==total['events'],
            'exposure_reconciles':abs(sum(r['years'] for r in rows)-total['years'])<1e-9,
            'all_18_months_available':bool((a['판정일']+pd.DateOffset(months=18)<=END).all()),
            'ci_contains_estimate':all(r['lo']<=r['rate']<=r['hi'] for r in rows),
            'road_counts_reconcile':sum(r['road_limited_count'] for r in rows)==total['road_limited_count'],
            'road_known_reconcile':sum(r['road_limited_n'] for r in rows)==total['road_limited_n'],
            'road_unknown_reconcile':sum(r['road_unknown_n'] for r in rows)==total['road_unknown_n'],
            'road_shares_use_known_only':all(abs(r['road_limited_count']/r['road_limited_n']*100-r['road_limited_pct'])<1e-10 for r in rows)}
    assert all(checks.values())
    (ROOT/'checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    print(json.dumps({'total':total,'main_districts':len(mainrows),'lowest':[{k:r[k] for k in ['name','n','events','rate','rate18']} for r in mainrows[:4]],
                      'highest':[{k:r[k] for k in ['name','n','events','rate','rate18']} for r in mainrows[-4:]],
                      'correlations':cor,'signal_types':summary['signal_types'],'checks':checks},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
