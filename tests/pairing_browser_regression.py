"""Playwright regression of the real game with a test-only state hook.

The hook is injected into an in-memory copy and its CSP hash is recalculated.
It is never added to the production index.html.
"""
from pathlib import Path
import base64
import hashlib
import os
import re
import shutil
from playwright.sync_api import sync_playwright

src = (Path(__file__).resolve().parents[1] / 'index.html').read_text(encoding='utf-8')
hook = """
  window.__pairTest={
    place(j,x,y){
      if(state!=='playing')throw new Error('Not playing: '+state);
      active=piece(shapes.find(shape=>shape.j===j));
      active.x=x;active.y=y;
      if(!valid(active))throw new Error('Actual piece-mask collision');
      lock();
    },
    snapshot(){
      return {state,score,lockCount,
        pending:[...pendingPairs.values()].map(p=>({...p})),
        ids:board.flat().filter(Boolean).map(c=>c.id),
        hint:el('word-hint').textContent};
    }
  };
"""
anchor = '  draw();drawPreview();\n})();'
assert src.count(anchor) == 1
instrumented = src.replace(anchor, '  draw();drawPreview();' + hook + '})();')
script = re.search(r'<script>([\s\S]*?)</script>', instrumented).group(1)
script_hash = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
instrumented, count = re.subn(
    r"script-src 'sha256-[^']+'",
    "script-src 'sha256-" + script_hash + "'",
    instrumented, count=1)
assert count == 1

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True,
        executable_path=os.getenv('CHROMIUM_EXECUTABLE') or shutil.which('chromium') or None)
    for width, height in ((390, 844), (360, 640), (844, 390)):
        page = browser.new_page(viewport={'width':width,'height':height},
                                is_mobile=True, has_touch=True)
        errors = []
        page.on('pageerror', lambda err: errors.append(str(err)))
        page.set_content(instrumented, wait_until='load')
        page.evaluate("""() => {
          window.securityViolations=[];
          document.addEventListener('securitypolicyviolation',
            e=>window.securityViolations.push(e.violatedDirective));
        }""")
        page.locator('#veil-button').click()
        assert '落下中' in page.locator('#piece-kind').inner_text()
        assert page.locator('#next-kind').inner_text() in ('母音','子音')
        if page.locator('#speech').get_attribute('aria-pressed') == 'true':
            page.locator('#speech').click()
        page.locator('#skip-next').click()
        assert '残り2回' in page.locator('#skip-next').inner_text()
        if width == 390:
            page.locator('#restart').click()
            page.evaluate("window.__pairTest.place('ㄷ',5,16)")
            page.evaluate("window.__pairTest.place('ㅓ',7,16)")
            info = page.evaluate('window.__pairTest.snapshot()')
            assert info['score'] == 100 and len(info['pending']) == 1, info
            assert 'パッチム待ち' in info['hint'] and 'あと2手' in info['hint'], info
            page.evaluate("window.__pairTest.place('ㄱ',6,19)")
            info = page.evaluate('window.__pairTest.snapshot()')
            assert info['state'] == 'clearing' and info['score'] == 300, info
            assert len(info['pending']) == 0
            assert page.locator('#word-title').inner_text() == '덕'
            page.wait_for_timeout(2400)
            page.locator('#restart').click()
            page.evaluate("window.__pairTest.place('ㄷ',5,16)")
            page.evaluate("window.__pairTest.place('ㅓ',7,16)")
            page.evaluate("window.__pairTest.place('ㄱ',0,19)")
            info = page.evaluate('window.__pairTest.snapshot()')
            assert len(info['pending']) == 1 and 'あと1手' in info['hint'], info
            page.evaluate("window.__pairTest.place('ㄱ',12,19)")
            info = page.evaluate('window.__pairTest.snapshot()')
            assert info['state'] == 'clearing' and len(info['pending']) == 0, info
            page.wait_for_timeout(2400)
            info = page.evaluate('window.__pairTest.snapshot()')
            assert info['state'] in ('playing','settling'), info
            assert not set(info['ids']).intersection({1,2}), info
        assert errors == [], errors
        assert page.evaluate('window.securityViolations') == []
        print('PASS',width,height,'real game notch and waiting-period regression')
        page.close()
    browser.close()
