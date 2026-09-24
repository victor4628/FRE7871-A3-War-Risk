"""Build the research report from final saved estimates, without hidden recalculation."""
import sys,json,re,math
from html import unescape
from pathlib import Path
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tmp/pythonpackages'))
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
GREEN='#254C45';LIGHT='#edf3f1';GREY='#55615e'
OUT=ROOT/'output';A=OUT/'analysis';PDF=OUT/'pdf';FIG=OUT/'figures'
PDF.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True)
s=json.loads((A/'summary.json').read_text());rank=json.loads((A/'rank_diagnostic.json').read_text())
r=pd.read_csv(A/'table2_sensitivities.csv');v=pd.read_csv(A/'table3_variance.csv');ass=pd.read_csv(A/'news_associations.csv');rob=pd.read_csv(A/'robustness.csv')
news=pd.read_csv(A/'news_daily.csv',index_col=0,parse_dates=True);lev=pd.read_csv(A/'market_levels.csv',index_col=0,parse_dates=True);chg=pd.read_csv(A/'market_changes.csv',index_col=0,parse_dates=True)
pairs=pd.read_csv(A/'event_control_pairs.csv',parse_dates=['H','L']);arts=pd.read_csv(A/'headline_scores.csv');cov=pd.read_csv(A/'market_coverage.csv')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':GREY,'text.color':'#222b28','axes.titleweight':'bold','axes.titlecolor':GREEN,'grid.alpha':.18,'figure.facecolor':'white'})
month=pd.read_csv(A/'corpus_monthly.csv',index_col=0);ai=pd.read_csv(ROOT/'data/raw/ai_gpr_country_monthly.csv');ai=ai[ai.Date.str.startswith('2026')]
fig,ax=plt.subplots(1,2,figsize=(9.5,3.1));x=np.arange(len(month))
ax[0].bar(x,month.articles,color='#cbd7d3',label='Eligible Iran headlines');ax[0].bar(x,month.war_articles,color=GREEN,label='War-relevant subset');ax[0].set_xticks(x,[i[-2:] for i in month.index]);ax[0].set_xlabel('Month in 2026');ax[0].set_ylabel('Headlines');ax[0].set_title('Measured news volume');ax[0].legend(fontsize=8,frameon=False)
ax[1].plot(np.arange(len(ai)),ai.Iran_all,'o-',color=GREEN);ax[1].set_xticks(np.arange(len(ai)),[i[5:7] for i in ai.Date]);ax[1].set_xlabel('Month in 2026');ax[1].set_ylabel('Published Iran AI-GPR index');ax[1].set_title('Independent monthly NLP benchmark');ax[1].grid(axis='y');fig.tight_layout();fig.savefig(FIG/'news_and_benchmark.png',dpi=190);plt.close(fig)
fig,ax=plt.subplots(1,2,figsize=(9.5,3.1));rr=r[r.series=='DGS10'].iloc[0]
h=chg.loc[pairs.H,'DGS2'];l=chg.loc[pairs.L,'DGS2']
ax[0].bar(['Control days','Event days'],[np.mean(l*l),np.mean(h*h)],color=['#b8c9c3',GREEN]);ax[0].set_ylabel('Mean squared yield change (bp squared)');ax[0].set_title('Treasury anchor has a weak shift')
ax[1].bar(range(1,8),rank['standardized_eigenvalues'],color=[GREEN if a>=0 else '#b98563' for a in rank['standardized_eigenvalues']]);ax[1].axhline(0,color=GREY,lw=.7);ax[1].set_title('Covariance-shift eigenvalues');ax[1].set_xlabel('Eigenvalue sorted from smallest');ax[1].set_ylabel('Standardized second-moment shift');fig.tight_layout();fig.savefig(FIG/'identification_checks.png',dpi=190);plt.close(fig)
fig,axes=plt.subplots(1,3,figsize=(9.5,3.0));groups=[(['DGS2','DGS10','BAMLC0A4CBBB','BAMLH0A0HYM2'],'Basis points'),(['SP500','GLD'],'Percent log return'),(['DCOILBRENTEU','DTWEXBGS'],'Native units')]
for ax,(keys,label) in zip(axes,groups):
    d=ass[(ass.lag==0)&ass.series.isin(keys)].set_index('series').loc[keys];y=np.arange(len(d))
    ax.errorbar(d.effect_per_sd_signed_news_change,y,xerr=np.vstack([d.effect_per_sd_signed_news_change-d.ci_lo,d.ci_hi-d.effect_per_sd_signed_news_change]),fmt='o',color=GREEN,capsize=3);ax.axvline(0,color=GREY,lw=.8);ax.set_yticks(y,keys,fontsize=8);ax.invert_yaxis();ax.set_xlabel(label);ax.grid(axis='x')
fig.suptitle('Signed-news associations with 95% HAC intervals',color=GREEN,fontsize=12);fig.tight_layout();fig.savefig(FIG/'news_sensitivity_intervals.png',dpi=190);plt.close(fig)
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='ReportTitle',fontName='Helvetica-Bold',fontSize=25,leading=29,textColor=colors.HexColor(GREEN),spaceAfter=13))
styles.add(ParagraphStyle(name='CoverTitle',fontName='Helvetica-Bold',fontSize=30,leading=35,textColor=colors.HexColor(GREEN),spaceAfter=18))
styles.add(ParagraphStyle(name='CoverSubtitle',fontName='Helvetica',fontSize=15,leading=20,textColor=colors.HexColor(GREY),spaceAfter=28))
styles.add(ParagraphStyle(name='Subhead',fontName='Helvetica-Bold',fontSize=14,leading=18,textColor=colors.HexColor(GREEN),spaceBefore=11,spaceAfter=7))
styles.add(ParagraphStyle(name='BodyR',fontName='Helvetica',fontSize=10.5,leading=14.5,spaceAfter=8,textColor=colors.HexColor('#242c29')))
styles.add(ParagraphStyle(name='SmallR',fontName='Helvetica',fontSize=8.3,leading=11.1,spaceAfter=6,textColor=colors.HexColor(GREY)))
styles.add(ParagraphStyle(name='TableR',fontName='Helvetica',fontSize=8.3,leading=10.6,textColor=colors.HexColor('#242c29')))
styles.add(ParagraphStyle(name='TableH',fontName='Helvetica-Bold',fontSize=8.3,leading=10.6,textColor=colors.white))
story=[];sections=[];md=[]
def txt(t):return escape(str(t))
def markdown_text(t):
    t=re.sub(r'<link href="([^"]+)"[^>]*>(.*?)</link>',lambda m:'['+m.group(2)+']('+unescape(m.group(1))+')',t)
    t=re.sub(r'<br\s*/?>','  \n',t)
    for tag,mark in [('b','**'),('i','*')]:t=t.replace('<'+tag+'>',mark).replace('</'+tag+'>',mark)
    return unescape(re.sub(r'<[^>]+>','',t))
def para(t,small=False):story.append(Paragraph(t,styles['SmallR' if small else 'BodyR']));md.append(markdown_text(t)+'\n')
def sub(t):story.append(Paragraph(txt(t),styles['Subhead']));md.append('### '+t+'\n')
def section(t):
    if story:story.append(PageBreak())
    story.append(Paragraph(txt(t),styles['ReportTitle']));sections.append(t);md.append('\n## '+t+'\n')
def table(headers,rows,widths):
    def cell(x):
        return '<link href="'+escape(x['href'],{'"':'&quot;'})+'" color="'+GREEN+'">'+txt(x['label'])+'</link>' if isinstance(x,dict) else txt(x)
    cells=[[Paragraph(txt(x),styles['TableH']) for x in headers]]+[[Paragraph(cell(x),styles['TableR']) for x in row] for row in rows]
    T=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT');T.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor(GREEN)),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor(LIGHT)]),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor(GREEN))]));story.append(T);story.append(Spacer(1,8))
    def mdcell(x):return '['+x['label']+']('+x['href']+')' if isinstance(x,dict) else markdown_text(str(x))
    md.append('| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(mdcell(x) for x in row)+' |' for row in rows)+'\n')
def figure(name):story.append(Image(str(FIG/name),width=512,height=512*plt.imread(FIG/name).shape[0]/plt.imread(FIG/name).shape[1]));story.append(Spacer(1,5))
def num(x,n=2):return f'{float(x):,.{n}f}'
def estse(z,prefix):
    est=float(z[prefix+'_effect_minus25bp']);se=float(z[prefix+'_robust_se_effect']);p=float(z[prefix+'_robust_p'])
    stars='***' if p<.01 else '**' if p<.05 else '*' if p<.10 else ''
    return num(est)+stars+' ('+num(se)+')'
def lookup(k):return r[r.series==k].iloc[0]
def ytd(k):
    d=lev[k].dropna();base=d.loc[:'2025-12-31'].iloc[-1];last=d.iloc[-1]
    return base,last,str(d.index[-1].date())

REPO_URL='https://github.com/victor4628/FRE7871-A3-War-Risk'
AUTHOR='Victor Chen'
STUDENT_ID='yc8027'
story.append(Spacer(1,90))
story.append(Paragraph('Iran War Risk and U.S. Financial Markets',styles['CoverTitle']))
story.append(Paragraph('An application of Rigobon and Sack (2003) to the 2026 Iran conflict',styles['CoverSubtitle']))
story.append(Paragraph('<b>Victor Chen</b><br/>NYU NetID: yc8027',styles['BodyR']))
story.append(Spacer(1,12))
story.append(Paragraph('<b>GitHub repository</b><br/><link href="'+REPO_URL+'" color="'+GREEN+'">'+REPO_URL+'</link>',styles['BodyR']))
story.append(Spacer(1,42))
story.append(Paragraph('Abstract',styles['Subhead']))
story.append(Paragraph('This report applies the heteroskedasticity identification design in <i>The Effects of War Risk on U.S. Financial Markets</i> to Iran-war news and daily U.S. market data in 2026. Headline analysis selects high-news and nearby lower-news dates. The study reproduces the paper\'s two single-instrument estimates and combined-IV estimate using available financial series, and reports standard errors and weak-identification diagnostics.',styles['BodyR']))
story.append(Paragraph('Markets moved substantially around the conflict, especially oil. The two-year Treasury variance shift is too weak to assign a precise causal sensitivity to a single Iran war-risk factor. These results document the limits of this replication while preserving the observed market response.',styles['BodyR']))
md.extend(['# Iran War Risk and U.S. Financial Markets\n','An application of Rigobon and Sack (2003) to the 2026 Iran conflict\n','**Victor Chen** | NYU NetID: yc8027\n','Repository: '+REPO_URL+'\n','## Abstract\n','This report applies the heteroskedasticity identification design in The Effects of War Risk on U.S. Financial Markets to Iran-war news and daily U.S. market data in 2026. Headline analysis selects high-news and nearby lower-news dates. The study reproduces the paper\'s two single-instrument estimates and combined-IV estimate using available financial series, and reports standard errors and weak-identification diagnostics.\n','Markets moved substantially around the conflict, especially oil. The two-year Treasury variance shift is too weak to assign a precise causal sensitivity to a single Iran war-risk factor. These results document the limits of this replication while preserving the observed market response.\n'])

section('Executive summary')
para('The core exercise follows the original paper\'s event/control heteroskedasticity design, two-year Treasury normalization, two single-instrument estimators, and combined-IV estimator. Iran-war news in 2026 replaces Iraq-war news; documented public-data proxies replace unavailable original financial series.')
para('<b>Main finding:</b> markets moved substantially around Iran-war developments, but this study cannot determine how much was caused by one Iran war-risk factor. The two-year Treasury anchor is weak, normalized estimates vary across instruments and events, and signed-news associations do not survive multiple-comparison correction. This does not show that the war had no market effect.')
table(['Coverage','Final study'],[['Financial variables','8 comparable outcomes plus the two-year Treasury anchor'],['Observed US sessions','178'],['News archive coverage','260 calendar days, no failed dates'],['Collected / eligible / war-relevant headlines','1,601 / 1,029 / 515'],['Matched event / control days','18 / 18; fewer pairs for some outcomes']],[178,334])
sub('Observed market changes are substantial')
rows=[]
for k in ['DGS2','DGS10','SP500','DCOILBRENTEU','BAMLH0A0HYM2','GLD']:
    b,e,d=ytd(k); unit=cov.set_index('series').loc[k,'unit'];change=(e-b)*100 if unit=='bp' else (e-b) if unit=='USD/bbl' else (e/b-1)*100
    rows.append([cov.set_index('series').loc[k,'variable'],num(change)+' '+unit,d])
table(['Variable','Change since Dec 31','Last observation'],rows,[225,155,132])
para('These are observed year-to-date changes, not effects attributable to the war. In particular, yields rose over the year while oil became more expensive; the 2003 assumption that an increase in war risk should be oriented toward a Treasury-yield fall cannot be imported automatically.',small=True)
oil0=chg.loc['2026-03-02','DCOILBRENTEU'];oil1=chg.loc['2026-03-03','DCOILBRENTEU'];y0=chg.loc['2026-03-02','DGS2'];y1=chg.loc['2026-03-03','DGS2']
para('<b>Conflict-onset example:</b> on March 2, the first US session after the February 28 outbreak, Brent rose $'+num(oil0)+'/bbl and the two-year Treasury yield rose '+num(y0,0)+' bp. Brent rose another $'+num(oil1)+' on March 3, a two-session gain of $'+num(oil0+oil1)+'; the yield rose '+num(y0+y1,0)+' bp. These are observed market moves, not causal war-effect estimates. The yield increase also makes the original paper\'s Treasury-fall normalization hard to interpret as an Iran-war-risk increase.',small=True)

section('How the two references fit together')
para('Rigobon (2003) supplies the identification principle: changing the relative variances of otherwise orthogonal structural shocks can reveal contemporaneous relationships, provided coefficients remain stable. Multiple regimes can supply additional restrictions and tests. A proportional rise in every shock variance adds little identifying information.')
para('Rigobon and Sack (2003) apply a narrower version to a latent war-news factor. They identify 17 news dates, compare them with nearby lower-news dates, normalize the factor to the two-year Treasury yield, and estimate effects on other financial variables. Their key restriction is that only the war factor variance changes between the two sets of dates.')
sub('The replicated financial model')
para('For financial changes x(t), let x(t) = b f(t) + u(t), where f is the unobserved war factor, b its stable reduced-form loadings, and u contains other common and idiosyncratic influences. With b(1) = 1 for the Treasury anchor, the identifying restriction is:')
para('<b>Delta Omega = Omega(H) - Omega(L) = Delta Var(f) b b transpose.</b>')
para('This implies a positive, rank-one covariance shift when H has greater war-shock variance. For outcome j, the two ratio estimators are <b>d1 = Delta Omega(1,j) / Delta Omega(1,1)</b> and <b>d2 = Delta Omega(j,j) / Delta Omega(1,j)</b>. The combined estimator uses both sign-switched instruments in 2SLS.')
sub('NLP selects the regimes and provides a separate proxy')
para('The news classifier identifies Iran war coverage, classifies threats, realized acts, energy exposure, and de-escalation, and measures unusually large news-flow changes. This avoids using observed market returns to choose the event dates. A separate signed-news regression estimates associations with a measurable text proxy; it does not replace the identifying assumptions of the latent-factor model.')
para('The factor scale is arbitrary. Multiplying each relative loading by -25 bp reproduces the original table normalization. In 2026 this is a conditional Treasury-yield scenario, not a verified increase in war probability. The loadings capture total contemporaneous market responses, including spillovers; they do not separate direct effects from transmission between assets.',small=True)

section('The financial dataset and replication departures')
para('The analysis uses a fixed snapshot of public daily observations, with retrieval details preserved in the source manifests. The common session calendar contains days with both Treasury and S&amp;P observations. No missing outcome is forward-filled; an event/control pair is dropped for an outcome if either daily change is unavailable.')
rows=[]
for _,z in cov.iterrows():rows.append([z.variable,z.series,z.unit,str(z.observed_changes)])
table(['Variable','Identifier','Change unit','N'],rows,[235,137,90,50])
para('Yields and spreads use first differences multiplied by 100 to convert percentage points to basis points. S&amp;P 500, GLD, and the broad dollar use 100 times log differences. Oil uses dollar changes per barrel.',small=True)
para('The main table now follows the original paper\'s US-market scope. Constant-maturity Treasury yields replace estimated off-the-run par yields, ICE option-adjusted spreads replace the original credit spreads, Brent spot replaces 12-month oil futures, and GLD adjusted returns replace a dollar bullion-price change. A comparable public on-the-run Treasury liquidity-premium series was not obtained and is explicitly omitted. European, Japanese, global-equity, emerging-market, VIX, bilateral-FX, and duplicate WTI extensions are excluded from the replication tables.',small=True)

section('News NLP and independent benchmark')
para('The corpus contains every dated article card retrieved from the Guardian Iran-tag archive between January 1 and September 17. URLs are deduplicated. Opinion, video, audio, gallery, and live-blog entries are excluded, as are headlines naming explicit financial-market outcomes. The primary classifier analyzes headlines; it does not claim full-story semantic or multilingual coverage.')
table(['Label','Examples of included terms'],[['Iran context','Iran, Tehran, Hormuz, Khamenei, Kharg, Natanz, IRGC'],['War relevance','War, strikes, missiles, military, nuclear, talks, ceasefire, blockade'],['Realized acts','Attacks, airstrikes, bombing, invasion, missiles, blockade'],['Threats','Warnings, nuclear, troop deployments, sanctions, escalation'],['Energy exposure','Hormuz, tankers, shipping, oil, gas, refineries, pipelines'],['De-escalation','Ceasefire, truce, peace, negotiation, deal, paused attacks']],[140,372])
para('A war-relevant headline must contain explicit Iran context. Clear metaphors are filtered. Labels overlap. Failed or rejected peace terms suppress the de-escalation flag. The score equals clip(max(0.25, acts + 0.5 threats + 0.75 energy + 0.5 failed peace) - effective peace, -1, 1). The daily news balance equals 100 times summed scores divided by eligible Iran-tag headlines. Empty news days have zero measured flow, not zero underlying risk.',small=True)
figure('news_and_benchmark.png')
para('Source: own archive NLP; published Iacoviello-Tong Iran AI-GPR monthly data. The published Iran index rises from 28.96 in January to 222.22 in March, about 7.67 times the January level. This corroborates the timing of the news surge, not the daily dictionary labels or a causal financial effect. September counts cover only 17 days. The eight available country-index months are not interpolated to daily observations.',small=True)

section('Event selection and nearby controls')
para('A session is eligible for H if its absolute change in log(1 + war-relevant headline count) is in the upper 20% of non-macro news innovations and it has at least two relevant headlines. The cutoff is '+num(s['H_cutoff'],3)+'. L must have an innovation at or below the median and no more than half the H headline count. Controls are selected nearest in time without replacement, within ten US sessions and the same prewar/wartime period.')
para('FOMC decision, CPI, and employment-report dates are excluded from both sets; a release on a closed-market date maps to the next joint session. This does not remove all other macroeconomic, tariff, earnings, or geopolitical news. Weekend and holiday news is accumulated into the next joint Treasury/S&amp;P session. Exact publication times are unavailable; the labels are retrospective.')
rows=[]
for _,p in pairs.iterrows():
    h=p.H;l=p.L;rows.append([str(h.date()),str(l.date()),str(int(news.loc[h,'war_articles'])),str(int(news.loc[l,'war_articles'])),num(p.H_innovation,2)])
table(['Event session H','Control session L','War news H','War news L','Innovation H'],rows,[117,117,88,88,102])
para('This is the complete source-paper Table 1 analogue. A session includes all mapped news, potentially from the preceding weekend; it is not a single signed event. Sources and individual labels are in headline_scores.csv. Both escalation and peace news qualify. Main-period prewar events are sparse; an isolated prewar regression does not meet the eight-pair reporting threshold.',small=True)
para('The March 2 event is paired with March 5 because the latter has lower measured headline innovation, yet Brent also rose $'+num(chg.loc['2026-03-05','DCOILBRENTEU'])+' on March 5. A low-news control can still contain substantial war-related market movement during an active conflict. This weakens the clean high-versus-low war-shock-variance comparison required by the paper.',small=True)

EVENTS={
 '2026-01-12':('Warnings about US intervention amid Iranian protests, alongside offers of talks.','warns US'),
 '2026-01-26':('US naval deployment and Iranian warnings of retaliation if strikes occur.','navy'),
 '2026-02-17':('Nuclear negotiators report agreement on guiding principles after renewed talks.','guiding principles'),
 '2026-02-19':('Disputes over base access and reporting on possible US attacks on Iran.','Diego Garcia'),
 '2026-02-23':('Iran prepares a nuclear proposal as Washington considers limited strikes.','counterproposal'),
 '2026-03-02':('Weekend US-Israeli attacks and Iranian retaliation expand into regional conflict.','US and Israel launch strikes'),
 '2026-03-16':('Threats against Kharg oil infrastructure and discussion of reopening Hormuz.','Kharg'),
 '2026-03-23':('Energy-infrastructure threats coincide with paused attacks and renewed diplomacy.','pauses'),
 '2026-03-24':('Pakistan pursues mediation while Britain proposes talks on reopening Hormuz.','Pakistan'),
 '2026-04-08':('A two-week ceasefire is announced amid disputes over shipping and regional scope.','two-week pause'),
 '2026-04-09':('Disagreement over Lebanon and the scope and durability of the ceasefire.','Lebanon'),
 '2026-05-04':('US naval action and ship guidance plans confront the Hormuz blockade.','Trump says US navy'),
 '2026-05-26':('Ceasefire proposals and prospective peace terms coexist with continuing attacks.','closer to peace'),
 '2026-06-08':('Iran-Israel exchanges of strikes raise questions about the ceasefire.','exchange strikes'),
 '2026-06-11':('Reports on strikes against water facilities and renewed uncertainty over the truce.','water facilities'),
 '2026-06-22':('Interrupted negotiations and nuclear inspection arrangements create mixed signals.','called off'),
 '2026-07-13':('Renewed US strikes and blockade announcements intensify the contest over Hormuz.','third night'),
 '2026-08-24':('Fresh US sanctions threats and Iranian retaliation warnings dominate coverage.','sanctions')}
for part in range(2):
    section('Selected war news developments'+(' from January to March' if part==0 else ' from April to August'))
    para('These descriptions summarize selected developments in each mapped event session. They are an audit aid, not additional selection criteria or a signed shock measure. A session can contain escalation and de-escalation together. Weekend stories appear in the next US session.')
    rows=[]
    for _,p in pairs.iloc[part*9:(part+1)*9].iterrows():
        day=str(p.H.date());desc,needle=EVENTS[day]
        a=arts[(arts.session==day)&arts.eligible&arts.relevant]
        match=a[a.headline.str.contains(needle,case=False,regex=False)]
        chosen=match.iloc[0] if len(match) else a.iloc[0]
        rows.append([day,desc,{'href':chosen.url,'label':'Article'}])
    table(['US session','Developments in the mapped news window','Traceability'],rows,[86,340,86])
    para('The source companion lists the representative article URL, original publication date inferred from its URL, mapped US session, and these research descriptions. All other articles behind each event remain in headline_scores.csv. The source link does not imply that the selected article captures every development on the date.',small=True)
event_rows=[]
for day,(desc,needle) in EVENTS.items():
    a=arts[(arts.session==day)&arts.eligible&arts.relevant];m=a[a.headline.str.contains(needle,case=False,regex=False)];z=m.iloc[0] if len(m) else a.iloc[0]
    event_rows.append({'event_session':day,'description':desc,'representative_article_url':z.url,'article_archive_date':z.archive_date,'control_session':str(pairs.set_index('H').loc[pd.Timestamp(day),'L'].date())})
pd.DataFrame(event_rows).to_csv(A/'event_sources.csv',index=False)

section('Table 2: Market Sensitivities')
para('<b>Scenario:</b> a latent-factor movement associated with a 25 bp decline in the US two-year yield. These estimates are supplied to replicate the original calculations; weak identification prevents treating them as calibrated increases in Iran war risk. An apparently precise combined-IV standard error does not resolve weak identification.')
rows=[]
for _,z in r.iterrows():rows.append([z.variable,z.unit,str(z.pairs),estse(z,'e1'),estse(z,'e2'),estse(z,'e3')])
table(['Outcome','Unit','Pairs','IV1 est. (SE)','IV2 est. (SE)','Both IVs est. (SE)'],rows,[166,48,35,88,88,87])
para('Heteroskedasticity-robust standard errors are in parentheses. Stars use two-sided normal-reference p values: * p &lt; 0.10, ** p &lt; 0.05, *** p &lt; 0.01. IV1 uses sign(H/L) times the Treasury change; IV2 uses sign(H/L) times the outcome change; the combined estimator uses both. The regressions follow the paper\'s zero-mean, no-intercept formulation. With a weak first stage, conventional SEs and stars can be misleading, so the next page also reports weak-IV-robust confidence sets.',small=True)
para('The S&amp;P conditional response is +1.85%, and the Brent response is -$25.33/bbl under the combined instruments. Their signs differ from the 2003 Iraq findings. Because the anchor is weak and the sign of a 2026 war shock is unverified, those signs are evidence against mechanically importing the original scenario, not evidence that war reliably benefits equities or lowers oil prices.',small=True)

section('Uncertainty and identification diagnostics')
para('The anchor second-moment shift is '+num(rr.delta_anchor_second_moment)+' bp squared. Its 95% circular pair-block bootstrap interval is ['+num(rr.delta_anchor_ci_lo)+', '+num(rr.delta_anchor_ci_hi)+']. The IV1 robust first-stage F statistic is '+num(rr.first_stage_robust_F_z1,2)+', far below customary strength benchmarks. Zero and negative variance shifts remain plausible.')
figure('identification_checks.png')
sub('Confidence sets preserve denominator uncertainty')
rows=[]
for k in ['DGS10','T10YIE','SP500','DCOILBRENTEU','DTWEXBGS','GLD']:
    z=lookup(k);rows.append([z.variable,z.AR_effect_confidence_set.replace(' U ',' or '),z.unit])
table(['Outcome','95% paired moment confidence set','Unit'],rows,[178,259,75])
para('Sets invert the IV1 difference-moment test using paired contributions with HAC covariance across the ordered pairs. They retain unbounded and disconnected regions. Thus a zero restriction can sometimes be rejected without identifying a finite magnitude or unique sign. Small-sample coverage is approximate. Percentile ratio intervals are also saved, but are not reliable replacements for unbounded sets.',small=True)
para('For seven outcomes and 17 common pairs, '+num(rank['rank1_residual_fraction']*100,1)+'% of the standardized covariance-shift energy remains outside its best positive rank-one approximation. The centered block-bootstrap diagnostic has p = '+num(rank['centered_block_bootstrap_p'],3)+'. The one-factor restriction is not rejected at 5%, but the test has little power with this sample; it does not verify homoskedastic other shocks, orthogonality, stable loadings, or that the factor is war risk.',small=True)

section('Comparison with the original Iraq war results')
para('The original combined-instrument results were scaled to a 25 bp fall in two-year yields. Only original outcomes with interpretable 2026 counterparts are compared below. Different instrument definitions, price units, calendars, and sample composition limit numerical comparability.')
orig={'DGS10':(-26,'bp'),'T10YIE':(-11,'bp'),'SP500':(-3.76,'%'),'BAMLC0A4CBBB':(5,'bp'),'BAMLH0A0HYM2':(34,'bp'),'DCOILBRENTEU':(.77,'USD/bbl futures'),'GLD':(1.30,'USD gold'),'DTWEXBGS':(-.44,'%')}
rows=[]
for k,(val,unit) in orig.items():
    z=lookup(k); rows.append([z.variable,num(val)+' '+unit,num(z.e3_effect_minus25bp)+' '+z.unit,'Proxy differs' if k in ['DCOILBRENTEU','GLD'] else 'Conditional only'])
table(['Outcome','Iraq 2003','Iran 2026','Comparison'],rows,[170,115,117,110])
sub('The original mechanisms need not carry over')
para('The 2003 paper found weaker equities, wider low-grade spreads, lower Treasury yields and inflation compensation, a weaker dollar, and higher year-ahead oil futures. Gold and Treasury liquidity premiums were not significantly affected. The 2026 application includes anticipation, active conflict, shipping disruption, negotiations, and repeated escalation over a longer period.')
para('Energy disruption could raise inflation pressure and yields while growth fears could lower them. This is an economic interpretation of competing channels, not an identified decomposition in this study. Under the covariance-only estimator the shock direction remains ambiguous, and the weak Treasury denominator magnifies that ambiguity.')
para('Consequently, the paper\'s 2003 elasticities should not be used as 2026 Iran portfolio stress parameters. The replicated 2026 point estimates are diagnostic outputs pending stronger identification, not replacement calibrated stress parameters.',small=True)

section('Table 3: Variance Calculations')
para('The paper\'s predicted shift for outcome j is d(j) squared times the anchor second-moment shift. The H share divides this by the observed H second moment. The all-session calculation divides the matched-event contribution by the sum of daily squared changes across available 2026 sessions. These are conditional algebraic calculations; causal lower-bound interpretation additionally requires valid identification and serial independence.')
rows=[]
for _,z in v.iterrows():rows.append([z.variable,num(z.L_second_moment,3),num(z.H_second_moment,3),num(z.predicted_variance_shift,3),num(z.raw_H_share_pct,1),num(z.raw_all_share_pct,1)])
table(['Outcome','L moment','H moment','Predicted shift','H %','All %'],rows,[190,65,65,72,60,60])
para('Moments have each outcome\'s daily-change unit squared. Financial outcomes have different units and cannot be compared by raw variance size. Outcome-specific missing pairs account for different samples.',small=True)
para('<b>No reported share is endorsed as an identified war-risk variance bound.</b> Weak loadings can generate implausible shares, while some observed outcome variances actually decline on H days. A numerically admissible percentage alone does not establish a causal decomposition. The CSV preserves raw results and flags percentages outside [0,100] rather than clipping them.',small=True)

section('Signed news sensitivities for replication variables')
para('This separate model regresses each daily financial change on standardized signed-news changes, attention changes, lagged financial changes, month effects, and scheduled macro-release indicators. HAC errors use five lags. One standard deviation of the news change is '+num(ass.risk_change_sd_index_points.iloc[0],2)+' news-index points; it is not a one-percentage-point change in war probability.')
rows=[]
for _,z in ass[ass.lag==0].iterrows():rows.append([z.variable,z.unit,num(z.effect_per_sd_signed_news_change,3),'['+num(z.ci_lo,3)+', '+num(z.ci_hi,3)+']',num(z.q_BH,3),str(z.N)])
table(['Outcome','Unit','Per news SD','95% HAC interval','FDR q','N'],rows,[180,57,75,110,52,38])
para('All contemporaneous intervals include zero. The smallest Benjamini-Hochberg adjusted q value is '+num(ass[ass.lag==0].q_BH.min(),3)+'. None of the 9 replication variables reaches q &lt; 0.05. Point estimates suggest higher oil prices and wider high-yield spreads alongside lower Treasury yields, but the data do not establish those responses statistically.',small=True)
para('Dictionary measurement error, single-outlet selection, post-event reporting, missing timestamps, mixed peace and conflict news, and confounding macro shocks limit interpretation. These results are associations with measured news flow, not structural causal estimates.',small=True)

section('Robustness and market timing')
rows=[]
labels={'top10':'Top 10% news innovations','top25':'Top 25% news innovations','next_session':'News mapped one session later','wartime':'Wartime only, local cutoff','exclude_opening_week':'Exclude March 2 to 6'}
for label in labels:
    d=rob[rob.specification==label].set_index('series');rows.append([labels[label],str(int(d.pairs.max())),num(d.loc['DGS10','e3_effect_minus25bp']),num(d.loc['SP500','e3_effect_minus25bp']),num(d.loc['DCOILBRENTEU','e3_effect_minus25bp']),num(d.loc['DTWEXBGS','e3_effect_minus25bp'])])
table(['Specification','Max pairs','10-year bp','S&P %','Brent USD','Dollar %'],rows,[172,47,75,69,78,71])
para('Each row uses the same -25 bp Treasury normalization. Cutoff changes redefine H and matching. Outcome samples can be smaller than the maximum pair count. The next-session rule shifts news features before selecting H/L. A prewar-only estimate is suppressed because it has fewer than eight matched pairs.',small=True)
figure('news_sensitivity_intervals.png')
para('The independent signed-news regressions also use next-session timing and a lead-news placebo. Their smallest corrected q values are '+num(ass[ass.lag==1].q_BH.min(),3)+' and '+num(ass[ass.lag==-1].q_BH.min(),3)+', respectively. No robust predictive association emerges. A nonsignificant lead placebo cannot establish causality, particularly when the contemporaneous signal is itself weak.',small=True)
para('FRED spot oil, Treasury, broad-dollar, and equity observations are not synchronized intraday. This timing limitation remains even after restricting the main table to the original paper\'s US-market scope.',small=True)

section('What the evidence supports')
para('<b>The 2026 Iran conflict coincides with substantial news intensity and market changes, but this public-data application does not isolate a precise single war-risk factor.</b> The March 2-3 Brent rise documents a large market move around the outbreak. The failed identification and statistically inconclusive signed-news regressions concern this model\'s ability to attribute and size the effect; they do not show that war had no financial effect.')
sub('Use the estimates as research diagnostics')
para('The original model\'s Treasury normalization is weak in this application. Some conditional estimates point in different directions across instruments or event definitions. The variance shares depend on those same unstable loadings. Therefore they cannot serve as reliable portfolio stress coefficients or as an attribution of year-to-date market returns.')
sub('Separate the most relevant channels in a stronger design')
para('A subsequent structural extension should distinguish threat and escalation news, actual energy-supply disruptions, and diplomacy or ceasefire news. For N financial variables and K latent common shocks, Rigobon\'s general method requires enough independent regimes and restricted structural covariances; adding extra NLP labels does not automatically identify additional financial shocks. Three or more independent regimes can help test stable loadings, but stronger economic restrictions are still needed.')
sub('The data that would most improve identification')
para('A licensed corpus of full news texts with original publication timestamps would allow semantic actor, event, novelty, and direction coding, source-balanced daily denominators, and multilingual coverage. Classifier scores should be checked against a held-out human-coded sample. News windows should be aligned to market closing times and screened for overlapping macro announcements without using market returns to select events.')
para('Intraday oil-futures curves, inflation-linked and nominal yields, credit instruments, and the original Treasury liquidity measure would reduce proxy and timing differences. Any alternative anchor must show a strong variance shift and have its shock sign established using independent news. An oil anchor could be useful for an energy-disruption factor, but would not by itself identify broader war risk.')
para('The repository contains the data snapshot, scripts, and tables for independent examination of event labels, estimator assumptions, and uncertainty calculations.',small=True)

section('Sources and reproducibility')
para('<b>References</b><br/>Rigobon, Roberto (2003). "Identification through Heteroskedasticity." <i>The Review of Economics and Statistics</i> 85(4), 777-792.<br/>Rigobon, Roberto and Brian Sack (2003). "The Effects of War Risk on U.S. Financial Markets." NBER Working Paper No. 9609. The event-selection design and Tables 1-3 provide the basis for this application.')
para('<b>News and NLP benchmark</b><br/>Guardian dated Iran-topic archive, January 1 to September 17, 2026. <link href="https://www.theguardian.com/world/iran">Guardian Iran archive</link>.<br/>Iacoviello, Matteo and Jonathan Tong (2026). The AI-GPR Index: Measuring Geopolitical Risk using Artificial Intelligence. Published monthly Iran-country series and methodology. <link href="https://www.matteoiacoviello.com/ai_gpr.html">Author data and paper</link>. This benchmark is descriptive and not an Iran-specific daily regressor.')
para('<b>Financial data</b><br/>FRED daily series DGS2, DGS10, T10YIE, SP500, BAMLC0A4CBBB, BAMLH0A0HYM2, DCOILBRENTEU, and DTWEXBGS. Federal Reserve, EIA, S&amp;P, and ICE BofA source series accessed via <link href="https://fred.stlouisfed.org">FRED</link>.<br/>Yahoo Finance daily adjusted-close history for GLD. The market sample ends September 17, 2026, with an earlier last observation for Brent. Download times and source URLs are recorded in the repository manifests.')
para('<b>Macro calendars</b><br/><link href="https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm">Federal Reserve FOMC calendar</link>; <link href="https://www.bls.gov/schedule/news_release/cpi.htm">BLS CPI calendar</link>; <link href="https://www.bls.gov/schedule/news_release/empsit.htm">BLS employment calendar</link>. Dates are preserved in summary.json and analyze.py.')
sub('Reproduce and inspect')
para('<b>Code, data, and report</b><br/><link href="'+REPO_URL+'">'+REPO_URL+'</link>')
para('README.md explains execution and departures. The scripts retrieve sources, score headlines, select H/L pairs, estimate all models, test algebra and units, and build this report from saved estimates. The principal tables are table2_sensitivities.csv, table3_variance.csv, and news_associations.csv. Source manifests record URLs and hashes. Bootstrap seeds are fixed; the main estimator uses 1,999 draws, and robustness tables use 399 draws.')
para('Validation recovered known positive and negative factor loadings in simulated data, verified equality of IV1 and the covariance ratio, checked disjoint matching and macro exclusions, checked basis-point conversions and the shock scale, and confirmed complete archive coverage. Verification establishes implementation correctness, not economic identification.',small=True)

def footer(canvas,doc):
    canvas.saveState();canvas.setStrokeColor(colors.HexColor(GREEN));canvas.setLineWidth(.55);canvas.line(50,43,562,43);canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor(GREY));canvas.drawString(50,30,'Victor Chen | yc8027');canvas.drawRightString(562,30,str(doc.page));canvas.restoreState()
dest=PDF/'iran_war_risk_2026.pdf'
doc=SimpleDocTemplate(str(dest),pagesize=(612,792),rightMargin=50,leftMargin=50,topMargin=48,bottomMargin=60,title='Iran War Risk and U.S. Financial Markets',author=AUTHOR,subject='Iran-war application of Rigobon and Sack (2003)')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
(OUT/'iran_war_risk_2026.md').write_text('\n'.join(md),encoding='utf-8')
from pypdf import PdfReader
pages=PdfReader(dest).pages
qa={'pages':len(pages),'cover_title':'Iran War Risk and U.S. Financial Markets','sections':sections,'text_characters':[len(p.extract_text() or '') for p in pages]}
(A/'report_structure.json').write_text(json.dumps(qa,indent=2));print(dest);print(json.dumps(qa,indent=2))
