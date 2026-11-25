# 자모 DROP — Hangul Drop

**Language / 言語 / 언어: [English](README.en.md) | [日本語](README.md) | [한국어](README.ko.md)**

**[▶ Play the game](https://keides2.github.io/hangul-drop-site/)** | **[Independent-tool evidence: CodeQL / ZAP (13 warning categories; Japanese)](INDEPENDENT_SECURITY_CHECKS.md)** | [Self-assessment](SECURITY_AUDIT.md)

Hangul Drop is a mobile-friendly falling-block puzzle game. Arrange Korean letters (*jamo*: consonants, vowels and final consonants, or *batchim*) to form syllables. It runs in a web browser; no installation or account is required.

## How to play

- Place an initial consonant and a vowel in the correct relative positions to form a syllable and earn **100 bonus points**.
- A completed two-jamo syllable stays for **two further block landings**. Add a valid final consonant below it during that time to earn **another 200 points**.
- Completed syllables remain visible for approximately **2.3 seconds** before clearing. When supported by the device, the browser can pronounce them in Korean.
- Clear a horizontal row by filling at least **13 of 16 cells**. Pieces may fall again and trigger combinations.
- Use **NEXT Skip** up to three times per game to replace the upcoming jamo.

**Controls:** On mobile, use the on-screen controls or swipe the board. On a keyboard, use arrow keys, Space (hard drop), `S` (skip NEXT) and `P` (pause). `♪` toggles sound effects, while `🔊` toggles Korean speech.

## A note about learning Hangul

Vertical vowels must appear on the right of the initial consonant, horizontal vowels below it, and a final consonant below the syllable. The game tolerates small alignment errors for playability: it is **not a definitive reference for Korean orthography or syllable composition**.

## Privacy and security

The game runs from **one HTML file**, without external JavaScript libraries, advertisements or analytics. Only the high score is stored locally in the browser's `localStorage`.

A limited source-code inspection and local browser runtime check did not find calls to external network APIs, recognizable embedded credentials or outbound requests during the tested actions. **These are self-assessment results, not independent certification or proof that the site has no vulnerabilities.** GitHub Pages hosting logs, security response headers, and the device's speech-synthesis service are outside the scope of those checks.

A passive ZAP scan of the live site reported **55 PASS rules, 13 warning categories and 0 FAIL rules**, including missing CSP and anti-clickjacking protections. **This does not prove the site is vulnerability-free.** See the **[external-tool results, original scan links and known limitations](INDEPENDENT_SECURITY_CHECKS.md)**, and the [reproducible self-assessment](SECURITY_AUDIT.md).

## Code and development

- Public game: <https://keides2.github.io/hangul-drop-site/>
- Game source: `index.html`; no build system or package installation is required.
- Source checks: `python3 tests/security_audit.py`.
- Optional browser smoke test: `python3 tests/browser_security_smoke.py` (requires Playwright and Chromium).
- This public repository started with a fresh Git history; the original private development history has not been imported.

**License:** No open-source license is granted at present. Public access to source code does not imply permission to redistribute or reuse it.
