import sys,json,urllib.request,urllib.parse
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data/raw'
start=int(datetime(2025,12,1,tzinfo=timezone.utc).timestamp()); end=int(datetime(2026,9,18,tzinfo=timezone.utc).timestamp())
def one(symbol):
    u=f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start}&period2={end}&interval=1d'
    try:
        b=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=35).read()
        (RAW/(symbol+'.json')).write_bytes(b)
        j=json.loads(b); print(symbol,len(j['chart']['result'][0]['timestamp']),flush=True)
        return {'symbol':symbol,'url':u,'bytes':len(b)}
    except Exception as e:return {'symbol':symbol,'url':u,'error':str(e)}
with ThreadPoolExecutor(max_workers=1) as p:r=list(p.map(one,['GLD']))
(RAW/'etf_manifest.json').write_text(json.dumps(r,indent=2),encoding='utf-8'); print(r)
