"""Validate estimator algebra and source coverage without mirroring implementation."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tmp/pythonpackages'));sys.path.insert(0,str(ROOT/'scripts'))
import numpy as np,pandas as pd
from analyze import moments,iv,cov_stats,ar_confidence
rng=np.random.default_rng(9609);n=100000
for loading in [2.,-3.]:
    a=np.c_[rng.normal(0,2,n),np.zeros(n)];b=np.c_[rng.normal(0,.5,n),np.zeros(n)]
    a[:,1]=loading*a[:,0]+rng.normal(0,1,n);b[:,1]=loading*b[:,0]+rng.normal(0,1,n)
    a[:,0]+=rng.normal(0,.4,n);b[:,0]+=rng.normal(0,.4,n)
    d,e1,e2=cov_stats(a,b);e3,se=iv(a,b,True);ez,_=iv(a,b,False)
    assert abs(e1-loading)<.03 and abs(e2-loading)<.03 and abs(e3-loading)<.03
    assert abs(ez-e1)<1e-10,'Instrument one must equal covariance ratio'
    assert se>0
OUT=ROOT/'output/analysis';s=json.loads((OUT/'summary.json').read_text())
news=pd.read_csv(OUT/'news_daily.csv',index_col=0,parse_dates=True)
p=pd.read_csv(OUT/'event_control_pairs.csv',parse_dates=['H','L'])
assert len(set(p.H)&set(p.L))==0,'Regimes must not overlap'
assert p.L.is_unique and p.H.is_unique,'Match without replacement'
for h,l in zip(p.H,p.L):
    assert not news.loc[h,'macro'] and not news.loc[l,'macro']
    assert news.loc[h,'complete'] and news.loc[l,'complete']
    assert (h<pd.Timestamp('2026-03-02'))==(l<pd.Timestamp('2026-03-02'))
levels=pd.read_csv(OUT/'market_levels.csv',index_col=0,parse_dates=True)
changes=pd.read_csv(OUT/'market_changes.csv',index_col=0,parse_dates=True)
assert changes.index.max()<=pd.Timestamp('2026-09-17')
check=levels.DGS2.diff().reindex(changes.index)*100
assert np.nanmax(np.abs(changes.DGS2-check))<1e-8,'Yield conversion must use basis points'
tables=pd.read_csv(OUT/'table2_sensitivities.csv')
assert np.allclose(tables.e1_beta*-25,tables.e1_effect_minus25bp)
assert s['archive_failures']==0,'Complete the news archive before delivery'
assert s['US_sessions']==len(changes)
result={'status':'passed','checks':['Known positive and negative factor loadings recovered in simulation','IV1 equals difference-of-second-moment estimator','Disjoint unique event and control days','Macro dates excluded and prewar/wartime matching enforced','Yield units and shock normalization checked','News archive coverage complete','Sample end obeyed'],'matched_pairs':len(p),'financial_variables':len(changes.columns)}
(OUT/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
