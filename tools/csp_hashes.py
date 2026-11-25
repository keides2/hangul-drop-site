#!/usr/bin/env python3
"""Check or refresh CSP hashes for the one-file game.

Usage:
  python3 tools/csp_hashes.py --check
  python3 tools/csp_hashes.py --update

CSP meta cannot set response-header-only directives such as frame-ancestors.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'index.html'


class TagInspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inline_style_attributes = []
        self.event_handlers = []
        self.remote_script_sources = []

    def handle_starttag(self, tag, attrs):
        for attr, value in attrs:
            if attr == 'style':
                self.inline_style_attributes.append(tag)
            if attr.startswith('on'):
                self.event_handlers.append((tag, attr))
            if tag == 'script' and attr == 'src':
                self.remote_script_sources.append(value)


def digest(source: str) -> str:
    return 'sha256-' + base64.b64encode(
        hashlib.sha256(source.encode('utf-8')).digest()
    ).decode('ascii')


def check_or_update(update=False):
    source = HTML.read_text(encoding='utf-8')
    styles = re.findall(r'<style>([\s\S]*?)</style>', source)
    scripts = re.findall(r'<script>([\s\S]*?)</script>', source)
    meta = re.search(r'<meta\s+http-equiv="Content-Security-Policy"\s+content="([^"]+)"\s*/?>', source)
    if len(styles) != 1 or len(scripts) != 1 or meta is None:
        raise ValueError('Expected exactly one style, one script, and one CSP meta tag')
    if meta.start() > source.index('<style>'):
        raise ValueError('CSP must precede executable or styled elements')
    inspector = TagInspector()
    inspector.feed(source)
    if inspector.inline_style_attributes or inspector.event_handlers or inspector.remote_script_sources:
        raise ValueError('Unexpected inline style attributes, HTML event handlers, or remote scripts')

    policy = meta.group(1)
    policies = [part.strip() for part in policy.split(';') if part.strip()]
    directives = dict(part.split(' ', 1) for part in policies)
    if len(policies) != len(directives):
        raise ValueError('Duplicate policy directives')
    required_none = ('default-src', 'base-uri', 'object-src', 'form-action',
                     'script-src-attr', 'style-src-attr', 'connect-src',
                     'img-src', 'font-src', 'media-src', 'frame-src',
                     'worker-src', 'manifest-src')
    for key in required_none:
        if directives.get(key) != "'none'":
            raise ValueError(f'Policy must enforce {key} none')
    if "'unsafe-inline'" in policy or "'unsafe-eval'" in policy:
        raise ValueError('unsafe-inline and unsafe-eval must not be permitted')
    if any(d in directives for d in ('frame-ancestors', 'sandbox', 'report-uri')):
        raise ValueError('Unsupported CSP meta directive')

    expected = {
        'script-src': "'" + digest(scripts[0]) + "'",
        'style-src': "'" + digest(styles[0]) + "'",
    }
    if update:
        new_policy = policy
        for key, value in expected.items():
            if key not in directives:
                raise ValueError('Missing directive: ' + key)
            new_policy = re.sub(r'\b' + key + r'\s+[^;]+', key + ' ' + value, new_policy, count=1)
        updated = source[:meta.start(1)] + new_policy + source[meta.end(1):]
        HTML.write_text(updated, encoding='utf-8')
        print('Updated CSP hashes in index.html')
    else:
        for key, value in expected.items():
            if directives.get(key) != value:
                raise ValueError(f'{key} hash does not match inline code; run python3 tools/csp_hashes.py --update')
        print('PASS: CSP hashes match 1 inline script and 1 inline stylesheet; strict directives intact')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--update', action='store_true')
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    try:
        check_or_update(update=args.update)
    except ValueError as exc:
        print('FAIL:', exc, file=sys.stderr)
        sys.exit(1)
