"""Verify public aggregate formulas and Spearman correlations; standard library only.

This checks published aggregates, not private house-level source records.
"""
from pathlib import Path
import csv, json, math

ROOT=Path(__file__).resolve().parent

def ranks(values):
    order=sorted(range(len(values)),key=values.__getitem__)
    result=[0.0]*len(values)
    i=0
    while i<len(order):
        j=i+1
        while j<len(order) and values[order[j]]==values[order[i]]:
            j+=1
        for k in order[i:j]:result[k]=(i+1+j)/2
        i=j
    return result

def spearman(x,y):
    rx,ry=ranks(x),ranks(y)
    mx,my=sum(rx)/len(rx),sum(ry)/len(ry)
    return sum((a-mx)*(b-my) for a,b in zip(rx,ry))/math.sqrt(
        sum((a-mx)**2 for a in rx)*sum((b-my)**2 for b in ry))

def close(a,b):
    assert math.isclose(float(a),float(b),rel_tol=1e-10,abs_tol=1e-9),(a,b)

def main():
    data=json.loads((ROOT/'public'/'data.json').read_text(encoding='utf-8'))
    with (ROOT/'public'/'seoul_district_rates.csv').open(encoding='utf-8-sig',newline='') as f:
        table=list(csv.DictReader(f))
    rows=data['districts'];total=data['total']
    assert len(rows)==len(table)==25
    by_name={r['name']:r for r in table}
    for r in rows:
        for key in ['n','events','years','rate','events18','years18','rate18',
                    'road_limited_count','road_limited_n','road_unknown_n','road_limited_pct']:
            close(r[key],by_name[r['name']][key])
        close(r['events']/r['years']*100,r['rate'])
        close(r['events18']/r['years18']*100,r['rate18'])
        close(r['road_limited_count']/r['road_limited_n']*100,r['road_limited_pct'])
        assert r['road_limited_n']+r['road_unknown_n']==r['n']
    for key in ['n','events','years','events18','years18','road_limited_count','road_limited_n','road_unknown_n']:
        close(sum(r[key] for r in rows),total[key])
    close(total['events']/total['years']*100,total['rate'])
    close(total['events18']/total['years18']*100,total['rate18'])
    close(total['road_limited_count']/total['road_limited_n']*100,total['road_limited_pct'])
    for scope in ['main','all']:
        chosen=[r for r in rows if r['road_limited_n']>0 and
                (scope=='all' or (r['n']>=30 and r['road_limited_n']>=30))]
        for period,column in [('full','rate'),('18','rate18')]:
            expected=data['road_relationship'][scope][period]
            assert len(chosen)==expected['n']
            close(spearman([r['road_limited_pct'] for r in chosen],[r[column] for r in chosen]),expected['rho'])
    print(json.dumps({'verified':True,'districts':25,'sample_houses':total['n'],
        'road_known':total['road_limited_n'],'road_limited':total['road_limited_count'],
        'road_share_pct':total['road_limited_pct'],'relationship':data['road_relationship']},indent=2))

if __name__=='__main__':main()
