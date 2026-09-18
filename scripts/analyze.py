"""Reproducible headline NLP, covariance-shift replication and HAC associations."""
import sys,json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tmp/pythonpackages'))
import numpy as np,pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
OUT=ROOT/'output/analysis'; OUT.mkdir(parents=True,exist_ok=True)
RAW=ROOT/'data/raw'
META={
 'DGS2':('US 2-year yield','bp','diff100'), 'DGS10':('US 10-year yield','bp','diff100'),
 'T10YIE':('US 10-year breakeven','bp','diff100'),
 'SP500':('S&P 500','%','log100'), 'BAMLC0A4CBBB':('US BBB OAS','bp','diff100'),
 'BAMLH0A0HYM2':('US high-yield OAS','bp','diff100'),
 'DCOILBRENTEU':('Brent spot','USD/bbl','diff'), 'DCOILWTICO':('WTI spot','USD/bbl','diff'),
 'DTWEXBGS':('Broad US dollar','%','log100'), 'VIXCLS':('VIX','points','diff'),
 'DEXUSEU':('EUR/USD','%','log100'), 'DEXJPUS':('USD/JPY','%','log100'),
 'NIKKEI225':('Nikkei 225 local close','%','log100'),
 'GLD':('Gold ETF GLD','%','log100'),'ACWI':('Global equity ETF ACWI','%','log100'),
 'FEZ':('Euro-area equity ETF FEZ','%','log100'),'EEM':('EM equity ETF EEM','%','log100')}
FOMC=['01-28','03-18','04-29','06-17','07-29','09-16']
CPI=['01-13','02-13','03-11','04-10','05-12','06-10','07-14','08-12','09-11']
JOBS=['01-09','02-11','03-06','04-03','05-08','06-05','07-02','08-07','09-04']
MACRO=pd.to_datetime(['2026-'+x for x in FOMC+CPI+JOBS])
# Final exploratory rules. Multi-label counts preserve ambiguity; no preregistration is claimed.
PAT={
 'iran_context':r'\b(iran\w*|tehran|hormuz|khamenei|kharg|natanz|irgc)\b',
 'metaphor':r'ticking bomb|social media wars|true missiles',
 'relevant':r'\b(war|wars|missiles?|airstrikes?|strikes?|bomb\w*|attack\w*|ceasefire|truce|peace|hormuz|naval|navy|military|nuclear|uranium|sanctions?|negotiat\w*|talks|blockad\w*|invasion|invad\w*|troops|drones?)\b',
 'acts':r'\b(airstrikes?|strikes?|bomb\w*|attack\w*|invasion|invad\w*|killed|kills|missiles?|drones?|blockad\w*)\b',
 'threats':r'\b(threat\w*|warn\w*|nuclear|uranium|military|troops|sanctions?|ultimatum|deploy\w*|escalat\w*)\b',
 'energy':r'\b(hormuz|blockad\w*|tankers?|shipping|oil|gas|energy|refiner\w*|pipelines?)\b',
 'peace':r'\b(ceasefire|truce|peace|talks|negotiat\w*|deal|diplomac\w*|de-escalat\w*|end(?:ing)? (?:the )?war|(?:halt|pause|postpone)\w* (?:the )?(?:war|strikes|attacks|iran.*attacks))\b',
 'failed_peace':r'\b(reject\w*|fail\w*|collaps\w*|violat\w*|breach\w*|denies|no|not|without|refus\w*|undermine\w*|called off)\b.{0,65}\b(ceasefire|talks|truce|peace|deal|negotiat\w*)\b|\b(ceasefire|talks|truce|peace|deal)\b.{0,50}\b(fail\w*|collaps\w*|violat\w*|breach\w*|reject\w*|called off|elusive|over)\b',
 'market':r'\b(stocks?|stock markets?|shares|ftse|s&p|wall street|financial markets?|bond yields?|inflation)\b|\b(oil|gas|gold|energy) prices?\b'}
def load_levels():
    cols={}
    for k in META:
        if k in ['GLD','ACWI','FEZ','EEM']:
            j=json.loads((RAW/(k+'.json')).read_text()); r=j['chart']['result'][0]
            dates=pd.to_datetime(r['timestamp'],unit='s',utc=True).tz_convert('America/New_York').tz_localize(None).normalize()
            vals=r['indicators'].get('adjclose',[{}])[0].get('adjclose',r['indicators']['quote'][0]['close'])
            cols[k]=pd.Series(vals,index=dates,dtype=float)
        else:
            d=pd.read_csv(RAW/(k+'.csv'),index_col=0,parse_dates=True); cols[k]=pd.to_numeric(d.iloc[:,0],errors='coerce')
    levels=pd.DataFrame(cols).sort_index()
    sessions=levels.index[levels.DGS2.notna() & levels.SP500.notna()]
    return levels.reindex(sessions)
def nlp(sessions):
    articles=json.loads((RAW/'guardian_articles.json').read_text(encoding='utf-8'))
    manifest=pd.DataFrame(json.loads((RAW/'guardian_manifest.json').read_text())).set_index('date')
    valid={pd.Timestamp(d) for d,r in manifest.iterrows() if pd.isna(r.get('error',np.nan))}
    rows=[]
    for a in articles:
        h=a['headline'].lower(); u=a['url']
        eligible=not any(x in u for x in ['/commentisfree/','/video/','/audio/','/gallery/','/live/']) and not re.search(PAT['market'],h)
        flags={k:bool(re.search(v,h)) for k,v in PAT.items()}
        flags['relevant']=flags['relevant'] and flags['iran_context'] and not flags['metaphor']
        peace=flags['peace'] and not flags['failed_peace']
        score=np.clip(max(.25,flags['acts']+0.5*flags['threats']+0.75*flags['energy']+0.5*flags['failed_peace'])-peace,-1,1) if flags['relevant'] else 0
        day=pd.Timestamp(a['archive_date']); session=sessions[sessions>=day]
        mapped=session[0] if len(session) else pd.NaT
        rows.append(a|flags|{'eligible':eligible,'peace_effective':peace,'signed_score':float(score),'session':mapped})
    art=pd.DataFrame(rows); art.drop(columns='standfirst').to_csv(OUT/'headline_scores.csv',index=False,encoding='utf-8')
    daily=[]
    for i,s in enumerate(sessions):
        if s<pd.Timestamp('2026-01-01'):continue
        prev=sessions[i-1] if i else s-pd.Timedelta(days=1)
        interval=pd.date_range(max(prev+pd.Timedelta(days=1),pd.Timestamp('2026-01-01')),s)
        complete=all(d in valid for d in interval)
        a=art[(art.session==s)&art.eligible]; n=len(a); rel=a[a.relevant]
        daily.append({'date':s,'complete':complete,'articles':n,'war_articles':len(rel),
            'acts':int(rel.acts.sum()),'threats':int(rel.threats.sum()),'energy':int(rel.energy.sum()),'peace':int(rel.peace_effective.sum()),
            'risk_balance':100*rel.signed_score.sum()/max(n,1),
            'attention':np.log1p(len(rel)) if complete else np.nan})
    d=pd.DataFrame(daily).set_index('date'); d.loc[~d.complete,'risk_balance']=np.nan
    d['attention_change']=d.attention.diff(); d['risk_change']=d.risk_balance.diff(); d['news_innovation']=d.attention_change.abs()
    macro_sessions=[sessions[sessions>=t][0] for t in MACRO if len(sessions[sessions>=t])]
    d['macro']=d.index.isin(macro_sessions); d.to_csv(OUT/'news_daily.csv')
    return art,d,manifest
def match(data,q=.8,lag=0,start=None,end=None):
    n=data.copy()
    if lag:
        for c in ['news_innovation','risk_change','attention_change','war_articles']:n[c]=n[c].shift(lag)
    if start:n=n.loc[start:]
    if end:n=n.loc[:end]
    n=n[n.news_innovation.notna() & ~n.macro]
    cutoff=n.news_innovation.quantile(q); median=n.news_innovation.median()
    h=n[(n.news_innovation>=cutoff)&(n.war_articles>=2)].sort_values('news_innovation',ascending=False)
    lows=set(n.index[n.news_innovation<=median]); pairs=[]
    fullidx=data.index
    for day,row in h.iterrows():
        if day in lows:lows.remove(day)
        p=fullidx.get_loc(day); pre=day<pd.Timestamp('2026-03-02')
        candidates=[l for l in lows if abs(fullidx.get_loc(l)-p)<=10 and ((l<pd.Timestamp('2026-03-02'))==pre) and n.loc[l,'war_articles']<=row.war_articles/2]
        if not candidates:continue
        lo=min(candidates,key=lambda l:(abs(fullidx.get_loc(l)-p),l))
        lows.remove(lo);pairs.append((day,lo))
    return sorted(pairs),float(cutoff)
def moments(a):return a.T@a/len(a) # Source-paper zero-mean second moments.
def iv(a,b,combined=False):
    n=len(a); data=np.vstack([a,b]); x=data[:,0]; y=data[:,1]
    sign=np.r_[np.ones(n),-np.ones(n)]; z=data*sign[:,None]
    z=z if combined else z[:,:1]
    W=np.linalg.pinv(z.T@z); zx=z.T@x; zy=z.T@y
    den=zx@W@zx; beta=float(zx@W@zy/den) if den>1e-15 else np.nan
    res=y-beta*x
    # Heteroskedastic robust covariance, with fixed regime membership.
    var=float((zx@W@(z.T@(z*(res**2)[:,None]))@W@zx)/(den**2)) if den>1e-15 else np.nan
    return beta,np.sqrt(max(var,0))
def cov_stats(a,b):
    d=moments(a)-moments(b); v=d[0,0]; c=d[0,1]; w=d[1,1]
    e1=c/v if abs(v)>1e-12 else np.nan; e2=w/c if abs(c)>1e-12 else np.nan
    return d,e1,e2
def ar_confidence(a,b):
    """Invert paired difference-moment tests, retaining unbounded/disjoint sets."""
    ga=a[:,0]*a[:,1]-b[:,0]*b[:,1]; gb=a[:,0]**2-b[:,0]**2
    n=len(ga); G=np.c_[ga,gb]; center=G-G.mean(0)
    S=center.T@center/n
    for lag in range(1,min(3,n)):
        C=center[lag:].T@center[:-lag]/n; S+=(1-lag/3)*(C+C.T)
    S=S/n; ma,mb=G.mean(0); c=stats.norm.ppf(.975)**2
    A=mb*mb-c*S[1,1]; B=-2*ma*mb+2*c*S[0,1]; C=ma*ma-c*S[0,0]
    disc=B*B-4*A*C
    if disc<0:intervals=[(-np.inf,np.inf)] if A<0 else []
    elif abs(A)<1e-12:intervals=[(-np.inf,-C/B)] if B>0 else [(-C/B,np.inf)]
    else:
        roots=sorted([(-B-np.sqrt(disc))/(2*A),(-B+np.sqrt(disc))/(2*A)])
        intervals=[tuple(roots)] if A>0 else [(-np.inf,roots[0]),(roots[1],np.inf)]
    effect=sorted([(-25*h,-25*l) for l,h in intervals])
    fmt=lambda x:'-inf' if x==-np.inf else '+inf' if x==np.inf else f'{x:.2f}'
    return ' U '.join('['+fmt(l)+', '+fmt(h)+']' for l,h in effect),float(2*stats.norm.sf(abs(ma)/max(np.sqrt(S[0,0]),1e-12)))
def rank_diagnostic(changes,pairs):
    cols=['DGS2','DGS10','T10YIE','SP500','BAMLH0A0HYM2','DCOILBRENTEU','DTWEXBGS']
    ps=[(h,l) for h,l in pairs if changes.loc[[h,l],cols].notna().all().all()]
    a=changes.loc[[h for h,l in ps],cols].to_numpy(); b=changes.loc[[l for h,l in ps],cols].to_numpy()
    if len(a)<8:return {'pairs':len(a),'error':'insufficient common pairs'}
    scale=np.sqrt(np.diag(moments(b)));a=a/scale;b=b/scale
    delta=moments(a)-moments(b)
    def fit(d):
        e,v=np.linalg.eigh(d); fitted=max(e[-1],0)*np.outer(v[:,-1],v[:,-1])
        return fitted,float(np.sum((d-fitted)**2)),e
    fitted,T,e=fit(delta); rng=np.random.default_rng(2026); draws=[]; n=len(a)
    for _ in range(1999):
        starts=rng.integers(0,n,size=int(np.ceil(n/3)));idx=((starts[:,None]+np.arange(3))%n).ravel()[:n]
        db=moments(a[idx])-moments(b[idx]);draws.append(fit(db-delta+fitted)[1])
    return {'pairs':n,'series':cols,'standardized_eigenvalues':e.tolist(),'rank1_residual_fraction':T/max(float(np.sum(delta**2)),1e-12),'centered_block_bootstrap_p':(1+sum(x>=T for x in draws))/2000,'test':'PSD rank-one Frobenius residual; centered circular pair-block bootstrap, block length 3, 1999 draws; approximate diagnostic'}
def estimate(changes,news,pairs,bootstrap=1999):
    rng=np.random.default_rng(7871); results=[]; variance=[]
    for k,(name,unit,_) in META.items():
        if k=='DGS2':continue
        ps=[(h,l) for h,l in pairs if changes.loc[[h,l],['DGS2',k]].notna().all().all()]
        if len(ps)<8:continue
        a=changes.loc[[h for h,l in ps],['DGS2',k]].to_numpy(); b=changes.loc[[l for h,l in ps],['DGS2',k]].to_numpy()
        d,e1,e2=cov_stats(a,b); e3,se3=iv(a,b,True)
        # Regime-specific demeaning robustness.
        dc,ec1,ec2=cov_stats(a-a.mean(0),b-b.mean(0))
        first=sm.OLS(np.r_[a[:,0],b[:,0]],sm.add_constant(np.r_[a[:,0],-b[:,0]])).fit(cov_type='HC1')
        F=float(first.tvalues[1]**2)
        boot=[]; dv=[]
        # Resample adjacent chronological pairs in circular blocks of three pairs.
        n=len(ps)
        for _ in range(bootstrap):
            starts=rng.integers(0,n,size=int(np.ceil(n/3)))
            idx=((starts[:,None]+np.arange(3))%n).ravel()[:n]
            da,be1,be2=cov_stats(a[idx],b[idx]); dv.append(da[0,0]); boot.append(be1*-25)
        ci=np.nanquantile(boot,[.025,.975]); dvci=np.quantile(dv,[.025,.975]); pr=float(np.mean(np.array(dv)>0))
        # Anderson-Rubin inversion: tests difference E[z(y-beta*x)] with z1.
        # This remains informative when the covariance-ratio denominator is weak.
        arset,arp=ar_confidence(a,b)
        r=results.append({'series':k,'variable':name,'unit':unit,'pairs':n,'e1_beta':e1,'e2_beta':e2,'e3_beta':e3,
            'e1_effect_minus25bp':-25*e1,'e2_effect_minus25bp':-25*e2,'e3_effect_minus25bp':-25*e3,
            'e3_robust_se_effect':25*se3,'e1_block_ci_lo':ci[0],'e1_block_ci_hi':ci[1],
            'centered_e1_effect':-25*ec1,'delta_anchor_second_moment':d[0,0], 'delta_anchor_ci_lo':dvci[0],'delta_anchor_ci_hi':dvci[1],
            'bootstrap_prob_positive_anchor_shift':pr,'first_stage_robust_F_z1':F,'AR_zero_p':arp,'AR_effect_confidence_set':arset,
            'relative_rank1_residual':abs(d[1,1]-e1*e1*d[0,0])/max(abs(d[1,1]),1e-12)})
        hvar=moments(a)[1,1]; lvar=moments(b)[1,1]; predicted=e3**2*d[0,0]
        allv=np.nanmean(changes[k]**2); hshare=predicted/hvar; allshare=(n/changes[k].notna().sum())*predicted/allv
        valid=d[0,0]>0 and 0<=hshare<=1 and 0<=allshare<=1
        variance.append({'series':k,'variable':name,'L_second_moment':lvar,'H_second_moment':hvar,'predicted_variance_shift':predicted,'raw_H_share_pct':hshare*100,'raw_all_share_pct':allshare*100,'admissible_bounds':valid})
    return pd.DataFrame(results),pd.DataFrame(variance)
def associations(changes,news):
    res=[]
    sd=news.risk_change.std()
    for lag in [0,1,-1]:
        for k,(name,unit,_) in META.items():
            n=pd.DataFrame({'y':changes[k],'r':news.risk_change.shift(lag)/sd,'a':news.attention_change.shift(lag),'ylag':changes[k].shift(1),'macro':news.macro.astype(float)})
            months=pd.get_dummies(n.index.month,prefix='m',dtype=float); months.index=n.index
            n=pd.concat([n,months.iloc[:,1:]],axis=1).dropna()
            if len(n)<30:continue
            x=n.drop(columns='y'); x=x.loc[:,x.nunique()>1]
            fit=sm.OLS(n.y,sm.add_constant(x,has_constant='add')).fit(cov_type='HAC',cov_kwds={'maxlags':5})
            if np.linalg.matrix_rank(fit.model.exog)<fit.model.exog.shape[1]:raise ValueError('Regression design lacks full rank')
            ci=fit.conf_int().loc['r'];res.append({'series':k,'variable':name,'unit':unit,'lag':lag,'N':len(n),'effect_per_sd_signed_news_change':fit.params['r'],'se_HAC':fit.bse['r'],'p':fit.pvalues['r'],'ci_lo':ci.iloc[0],'ci_hi':ci.iloc[1],'R2':fit.rsquared,'risk_change_sd_index_points':sd})
    r=pd.DataFrame(res)
    for lag in [0,1,-1]:
        idx=r.lag==lag;r.loc[idx,'q_BH']=multipletests(r.loc[idx,'p'],method='fdr_bh')[1]
    return r
def main():
    levels=load_levels(); changes=pd.DataFrame(index=levels.index)
    for k,(_,_,trans) in META.items():
        changes[k]=np.log(levels[k]).diff()*100 if trans=='log100' else levels[k].diff()*(100 if trans=='diff100' else 1)
    changes=changes.loc['2026-01-02':'2026-09-17']; levels.to_csv(OUT/'market_levels.csv'); changes.to_csv(OUT/'market_changes.csv')
    art,news,manifest=nlp(levels.index); news=news.reindex(changes.index)
    pairs,cut=match(news)
    p=pd.DataFrame(pairs,columns=['H','L']);p['H_innovation']=[news.loc[h,'news_innovation'] for h,l in pairs];p['L_innovation']=[news.loc[l,'news_innovation'] for h,l in pairs];p.to_csv(OUT/'event_control_pairs.csv',index=False)
    r,v=estimate(changes,news,pairs); r.to_csv(OUT/'table2_sensitivities.csv',index=False);v.to_csv(OUT/'table3_variance.csv',index=False)
    (OUT/'rank_diagnostic.json').write_text(json.dumps(rank_diagnostic(changes,pairs),indent=2))
    assoc=associations(changes,news);assoc.to_csv(OUT/'news_associations.csv',index=False)
    robustness=[]
    for label,q,lag,start,end in [('top10',.9,0,None,None),('top25',.75,0,None,None),('next_session',.8,1,None,None),('prewar',.8,0,None,'2026-02-27'),('wartime',.8,0,'2026-03-02',None),('exclude_opening_week',.8,0,None,None)]:
        pp,_=match(news,q,lag,start,end)
        if label=='exclude_opening_week':pp=[(h,l) for h,l in pp if not (pd.Timestamp('2026-03-02')<=h<=pd.Timestamp('2026-03-06') or pd.Timestamp('2026-03-02')<=l<=pd.Timestamp('2026-03-06'))]
        rr,_=estimate(changes,news,pp,bootstrap=399)
        if len(rr):rr['specification']=label;robustness.append(rr)
    if robustness:pd.concat(robustness).to_csv(OUT/'robustness.csv',index=False)
    coverage=pd.DataFrame({'series':list(META),'variable':[v[0] for v in META.values()],'unit':[v[1] for v in META.values()],'observed_changes':[int(changes[k].notna().sum()) for k in META]});coverage.to_csv(OUT/'market_coverage.csv',index=False)
    monthly=art[art.eligible].groupby(art.archive_date.str[:7]).agg(articles=('url','size'),war_articles=('relevant','sum'));monthly.to_csv(OUT/'corpus_monthly.csv')
    summary={'sample_start':str(changes.index.min().date()),'sample_end':str(changes.index.max().date()),'US_sessions':len(changes),'articles_collected':len(art),'eligible_headlines':int(art.eligible.sum()),'war_headlines':int((art.eligible&art.relevant).sum()),'archive_days':len(manifest),'archive_failures':int(manifest.get('error',pd.Series()).notna().sum()),'complete_news_sessions':int(news.complete.fillna(False).sum()),'news_change_sessions':int(news.news_innovation.notna().sum()),'H_cutoff':cut,'pairs':len(pairs),'rules':PAT,'macro_dates':[str(x.date()) for x in MACRO],'macro_session_dates':[str(t.date()) for t in news.index[news.macro]]}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['rules','macro_dates']},indent=2))
    if len(r):print(r[['variable','pairs','e1_effect_minus25bp','e2_effect_minus25bp','e3_effect_minus25bp','delta_anchor_second_moment','first_stage_robust_F_z1']].to_string(index=False))
    print(assoc[assoc.lag==0][['variable','effect_per_sd_signed_news_change','ci_lo','ci_hi','q_BH','N']].to_string(index=False))
if __name__=='__main__':main()
