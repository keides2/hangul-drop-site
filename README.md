# Hangul Drop — public game site

A standalone browser game for arranging Korean Hangul jamo into syllables.

## Play

Open `index.html` in a browser. The game is packaged as a single HTML document and does not require an account, web API, or external JavaScript libraries.

- Mobile: on-screen movement, rotation, drop, and NEXT skip buttons.
- Keyboard: arrow keys, Space for hard drop, `S` to skip NEXT, `P` to pause.
- Rules: form syllables, earn bonuses, clear filled rows, and continue after gravity settles.
- Korean pronunciations use the browser's speech synthesis engine when supported.
- Completed 2-jamo and 3-jamo syllables remain visible for about 3 seconds to allow reading.

## Privacy and data

This static site does not send game information to a server and contains no analytics or external scripts. The browser can store a local best-score value via `localStorage`.

This is a falling-block game with approximate placement rules. It is **not** a complete reference for formal Hangul orthography.

## Publication

Publish these files from the root of a fresh public Git repository with a fresh, email-private commit history. Do **not** make the original private development repository public: its historical commits contain personal author metadata.

No software license is granted by this README. Contact the repository owner before reusing the source.
