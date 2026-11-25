"""Chromium regression: gameplay succeeds under CSP; script injection and I/O fail.

Run after: pip install playwright && python -m playwright install chromium
"""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

HTML = (Path(__file__).resolve().parents[1] / 'index.html').read_text(encoding='utf-8')

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=os.environ.get("CHROMIUM_EXECUTABLE") or None)
    for width, height in ((390, 844), (360, 640), (844, 390)):
        page = browser.new_page(viewport={'width': width, 'height': height},
                                is_mobile=True, has_touch=True)
        errors, requests = [], []
        page.on('pageerror', lambda err: errors.append(str(err)))
        page.on('request', lambda req: requests.append(req.url))
        page.set_content(HTML, wait_until='load')
        page.evaluate("""() => {
            window.cspViolations = [];
            document.addEventListener('securitypolicyviolation',
              e => window.cspViolations.push(e.violatedDirective));
        }""")
        assert page.locator('#veil').is_visible()
        assert page.locator('.brand-drop').evaluate(
            '(el) => getComputedStyle(el).color') == 'rgb(111, 224, 238)'
        assert page.locator('#speech-test').evaluate(
            '(el) => getComputedStyle(el).borderTopWidth') == '1px'
        page.locator('#veil-button').click()
        assert page.locator('#veil').is_hidden()
        page.locator('#skip-next').click()
        assert '残り2回' in page.locator('#skip-next').inner_text()
        page.locator('#sound').click()
        assert page.locator('#sound').get_attribute('aria-pressed') == 'true'
        page.locator('#sound').click()
        assert page.locator('#sound').get_attribute('aria-pressed') == 'false'
        page.locator('#left').click()
        page.locator('#right').click()
        page.locator('#drop').click()
        page.keyboard.press('s')
        assert '残り1回' in page.locator('#skip-next').inner_text()
        assert not errors, errors
        assert not requests, requests
        assert not page.evaluate('window.cspViolations')

        if width == 390:
            # This script must not execute; it does not match the CSP hash.
            page.evaluate("""() => {
                const e = document.createElement('script');
                e.textContent = 'window.UNSAFE_SCRIPT_RAN=true';
                document.head.appendChild(e);
            }""")
            page.wait_for_timeout(100)
            assert page.evaluate('window.UNSAFE_SCRIPT_RAN === undefined')
            assert 'script-src-elem' in page.evaluate('window.cspViolations')
            page.evaluate("""() => {
                const e = document.createElement('style');
                e.textContent = 'body { color: red !important }';
                document.head.appendChild(e);
            }""")
            page.wait_for_timeout(100)
            assert 'style-src-elem' in page.evaluate('window.cspViolations')
            page.evaluate("""() => {
                fetch('https://example.com/').catch(() => {});
            }""")
            page.wait_for_timeout(100)
            assert 'connect-src' in page.evaluate('window.cspViolations')
            assert not requests, requests
        print(f'PASS: {width}x{height} gameplay; no benign CSP violations')
        page.close()
    browser.close()
print('PASS: injected script, injected style, and outbound fetch were blocked')
