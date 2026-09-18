"""Download public source data. No credentials required; preserve raw responses."""
import sys, json, hashlib, urllib.request, urllib.parse, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'; RAW.mkdir(parents=True,exist_ok=True)
tasks=[]
for f in ['ai_gpr_data_daily.csv','ai_gpr_country_monthly.csv','ai_gpr_country_eventtype_monthly.csv']:
    tasks.append((f,'https://www.matteoiacoviello.com/ai_gpr_files/'+f))
tasks.append(('AI_GPR_PAPER.pdf','https://www.matteoiacoviello.com/research_files/AI_GPR_PAPER.pdf'))
for s in ['DGS2','DGS10','T10YIE','SP500','BAMLC0A4CBBB','BAMLH0A0HYM2','DCOILBRENTEU','DCOILWTICO','DTWEXBGS','VIXCLS','DEXUSEU','DEXJPUS','NIKKEI225']:
    tasks.append((s+'.csv','https://fred.stlouisfed.org/graph/fredgraph.csv?'+urllib.parse.urlencode({'id':s,'cosd':'2025-12-01','coed':'2026-09-17'})))
def fetch(task):
    name,url=task
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 Research replication'})
        b=urllib.request.urlopen(req,timeout=55).read(); (RAW/name).write_bytes(b)
        return {'file':name,'url':url,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'retrieved_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    except Exception as e:return {'file':name,'url':url,'error':str(e)}
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(fetch,tasks))
    (RAW/'manifest.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    for r in results:print(r['file'],r.get('bytes',r.get('error')))
    q='Iran (war OR military OR missile OR nuclear OR ceasefire OR Hormuz) sourcelang:english'
    url='https://api.gdeltproject.org/api/v2/doc/doc?'+urllib.parse.urlencode({'query':q,'mode':'artlist','format':'json','maxrecords':250,'sort':'datedesc','startdatetime':'20260101000000','enddatetime':'20260108000000'})
    print('GDELT TEST',fetch(('gdelt_test.json',url)))
