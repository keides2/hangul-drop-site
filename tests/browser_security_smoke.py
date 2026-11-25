"""Optional Chromium runtime smoke test (the local HTML, not the live server)."""
import asyncio, json
from pathlib import Path
from shutil import which
from urllib.parse import urlsplit
from playwright.async_api import async_playwright

HTML=(Path(__file__).resolve().parents[1]/'index.html').read_text(encoding='utf-8')
async def main():
    results=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,executable_path=which('chromium') or None)
        try:
            for w,h in ((390,844),(360,640),(844,390)):
                page=await browser.new_page(viewport={'width':w,'height':h},is_mobile=True,has_touch=True)
                errors=[];external=[]
                page.on('pageerror',lambda e: errors.append(str(e)))
                page.on('request',lambda req: external.append(req.resource_type) if urlsplit(req.url).scheme not in ('file','data','blob') else None)
                await page.set_content(HTML,wait_until='load')
                assert await page.locator('#veil').is_visible()
                assert await page.locator('#sound').inner_text()=='♪'
                await page.locator('#veil-button').click()
                assert await page.locator('#veil').is_hidden()
                await page.locator('#skip-next').click()
                assert '残り2回' in await page.locator('#skip-next').inner_text()
                await page.locator('#sound').click()
                assert await page.locator('#sound').get_attribute('aria-pressed')=='true'
                await page.locator('#sound').click()
                assert await page.locator('#sound').get_attribute('aria-pressed')=='false'
                await page.locator('#left').click()
                await page.locator('#right').click()
                await page.locator('#drop').click()
                await page.keyboard.press('s')
                assert '残り1回' in await page.locator('#skip-next').inner_text()
                await page.wait_for_timeout(250)
                assert not errors,errors
                assert not external,external
                results.append({'viewport':f'{w}x{h}','js_errors':len(errors),'external_requests':len(external),'controls':'PASS'})
                await page.close()
        finally:
            await browser.close()
    print(json.dumps({'result':'PASS','scope':'Local HTML executed in Chromium; not the live GitHub Pages server','screens':results},ensure_ascii=False,indent=2))

if __name__=='__main__':
    asyncio.run(main())
