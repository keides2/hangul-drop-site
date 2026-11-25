#!/usr/bin/env python3
"""Reproducible checks of the public single-file game (not a security certification)."""
from html.parser import HTMLParser
from pathlib import Path
import re, json, sys

ROOT = Path(__file__).resolve().parents[1]
game = (ROOT / 'index.html').read_text(encoding='utf-8')

class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs=[]; self.inline_scripts=0; self.handlers=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='script':
            if 'src' not in d:self.inline_scripts+=1
        for k,v in attrs:
            if k.lower().startswith('on') and v:self.handlers.append((tag,k))
        if tag in {'script','img','iframe','audio','video','source','embed','object','track'}:
            for name in ('src','data','poster'):
                if d.get(name):self.refs.append((tag,d[name]))
        if tag=='link' and d.get('href'):self.refs.append((tag,d['href']))

parser=Assets()
parser.feed(game)
patterns={
    'outbound network APIs': r'\b(?:fetch\s*\(|XMLHttpRequest\b|WebSocket\b|EventSource\b|sendBeacon\s*\(|navigator\.sendBeacon\b)',
    'dynamic JS execution': r'\b(?:eval\s*\(|new\s+Function\s*\(|setTimeout\s*\(\s*["\x27]|setInterval\s*\(\s*["\x27])',
    'HTML injection sinks': r'\b(?:innerHTML\s*=|outerHTML\s*=|insertAdjacentHTML\s*\(|document\.write\s*\()',
    'embedded URL': r'(?:https?://|wss?://|//[a-z0-9.-]+\.[a-z]{2,}/)',
    'cookie or service worker': r'\b(?:document\.cookie\b|serviceWorker\b)',
    'script navigation': r'\b(?:window\.open\s*\(|location\.href\s*=|location\.replace\s*\()',
}
counts={name:len(re.findall(pattern,game,re.I)) for name,pattern in patterns.items()}
# These patterns are deliberately limited; unknown token formats can be missed.
secrets=[
    r'gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{50,}',
    r'AKIA[0-9A-Z]{16}',
    r'AIza[0-9A-Za-z_-]{30,}',
    r'\bsk-[A-Za-z0-9_-]{20,}\b',
    r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
]
files=[p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts]
email=re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',re.I)
credential_hits=0;email_hits=0
for f in files:
    s=f.read_text(encoding='utf-8')
    credential_hits+=sum(len(re.findall(p,s)) for p in secrets)
    email_hits+=int(email.search(s) is not None)
storage_keys=sorted(set(re.findall(r'localStorage\.(?:getItem|setItem)\(\s*["\x27]([^"\x27]+)',game)))
read_count=len(re.findall(r'localStorage\.getItem\s*\(',game))
write_count=len(re.findall(r'localStorage\.setItem\s*\(',game))
errors=[]
if parser.refs:errors.append('Unexpected HTML resource reference')
if parser.inline_scripts!=1:errors.append('Unexpected inline script count')
if parser.handlers:errors.append('HTML inline event handlers')
if any(counts.values()):errors.append('Potentially risky API patterns')
if credential_hits:errors.append('Possible credentials')
if email_hits:errors.append('Email addresses in public source')
if storage_keys!=['jamo-drop-syllableclear-best'] or read_count!=1 or write_count!=1:
    errors.append('Unexpected localStorage access')
result={
  'result':'PASS' if not errors else 'FAIL',
  'scope':'public repository source; not live HTTP headers or host systems',
  'public_files_inspected':len(files),
  'external_html_resources':len(parser.refs),
  'inline_scripts':parser.inline_scripts,
  'html_event_handlers':len(parser.handlers),
  'risky_pattern_counts':counts,
  'credential_pattern_hits':credential_hits,
  'email_file_hits':email_hits,
  'localStorage_reads':read_count,
  'localStorage_writes':write_count,
  'localStorage_keys':storage_keys,
  'errors':errors,
}
print(json.dumps(result,ensure_ascii=False,indent=2))
sys.exit(int(bool(errors)))
