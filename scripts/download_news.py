"""Collect the complete dated Guardian Iran tag archive, without market selection."""
import json, sys, re, time, hashlib, urllib.request, gzip
from pathlib import Path
from datetime import date,timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import unescape
ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data/raw/guardian'; RAW.mkdir(parents=True,exist_ok=True)
MONTHS=['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
def archive(d):
    url=f'https://www.theguardian.com/world/iran/{d.year}/{MONTHS[d.month-1]}/{d.day:02d}/all'
    dest=RAW/(str(d)+'.html.gz')
    try:
        if dest.exists(): b=gzip.decompress(dest.read_bytes())
        else:
            time.sleep(1.25)
            req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
            b=urllib.request.urlopen(req,timeout=40).read(); dest.write_bytes(gzip.compress(b))
        s=b.decode('utf-8'); out=[]
        # Each article card starts at data-id. Ignore menus and duplicate overlay links.
        for m in re.finditer(r'data-id="([^"]+)"',s):
            block=s[m.end():s.find('data-id="',m.end()) if s.find('data-id="',m.end())>=0 else len(s)]
            title=re.search(r'<span class="js-headline-text">(.*?)</span>',block,re.S)
            if not title:continue
            path=m.group(1); match=re.search(r'/(2026)/(\w{3})/(\d{2})/', '/'+path)
            if not match:continue
            actual=date(2026,MONTHS.index(match.group(2))+1,int(match.group(3)))
            if actual!=d:continue # Empty dated archives may fall back to another date.
            stand=re.search(r'<div class="fc-item__standfirst">(.*?)</div>',block,re.S)
            clean=lambda x:unescape(re.sub('<[^>]*>',' ',x)).strip()
            out.append({'archive_date':str(d),'url':'https://www.theguardian.com/'+path,'headline':clean(title.group(1)),'standfirst':clean(stand.group(1)) if stand else '', 'archive_url':url})
        return {'date':str(d),'url':url,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'articles':out}
    except Exception as e:return {'date':str(d),'url':url,'error':str(e),'articles':[]}
if __name__=='__main__':
    dates=[date(2026,1,1)+timedelta(days=i) for i in range((date(2026,9,17)-date(2026,1,1)).days+1)]
    # Freeze the requested 2026 corpus period; successful pages are reused on retries.
    results=[]
    with ThreadPoolExecutor(max_workers=1) as pool:
        fs=[pool.submit(archive,d) for d in dates]
        for i,f in enumerate(as_completed(fs),1):
            results.append(f.result())
            if i%30==0:print('Archives',i,'articles',sum(len(r['articles']) for r in results),flush=True)
    results.sort(key=lambda r:r['date'])
    rows={a['url']:a for r in results for a in r['articles']}
    (ROOT/'data/raw/guardian_articles.json').write_text(json.dumps(list(rows.values()),ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'data/raw/guardian_manifest.json').write_text(json.dumps([{k:v for k,v in r.items() if k!='articles'}|{'article_count':len(r['articles'])} for r in results],indent=2),encoding='utf-8')
    print('DONE',len(rows),'failures',sum('error' in r for r in results))
