"""Check static references (CSS url(...) and template {% static '...' %})
and verify each referenced path is discoverable by Django staticfiles finders.

Run from project root (it bootstraps Django):
    python scripts/check_static_refs.py
"""
import re
import sys
from pathlib import Path


def bootstrap_django():
    # Configure DJANGO_SETTINGS_MODULE and setup
    import os

    # ensure project root is on sys.path
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmaster.settings')
    try:
        import django

        django.setup()
    except Exception as exc:
        print('Failed to bootstrap Django:', exc)
        sys.exit(1)


def find_static_references(root):
    css_url_re = re.compile(r"url\((?:'|\")?(.*?)(?:'|\")?\)")
    template_static_re = re.compile(r"\{\%\s*static\s+['\"](.*?)['\"]\s*\%\}")
    refs = set()

    for path in Path(root).rglob('*.css'):
        try:
            text = path.read_text(encoding='utf-8')
        except Exception:
            continue
        for m in css_url_re.findall(text):
            # ignore external urls
            if m.startswith('http') or m.startswith('data:'):
                continue
            refs.add(m.strip())

    for path in Path(root).rglob('*.html'):
        try:
            text = path.read_text(encoding='utf-8')
        except Exception:
            continue
        for m in template_static_re.findall(text):
            refs.add(m.strip())

    return refs


def check_refs(refs):
    from django.contrib.staticfiles import finders
    from django.core.exceptions import SuspiciousFileOperation

    missing = []
    found = []
    project_root = Path(__file__).resolve().parents[1]
    for r in sorted(refs):
        # normalize leading slashes
        rr = r.lstrip('/')
        located = None
        try:
            located = finders.find(rr)
        except SuspiciousFileOperation:
            # rr likely contains '..' segments; fall back to basename search below
            located = None
        except Exception:
            located = None

        if not located:
            # fallback: try to find by basename anywhere under project static folders
            name = Path(rr).name
            matches = list(project_root.rglob(name))
            # filter out venv and staticfiles output
            matches = [m for m in matches if 'site-packages' not in str(m) and 'staticfiles' not in str(m)]
            if matches:
                # prefer matches under any 'static' directory
                preferred = None
                for m in matches:
                    if '/static/' in str(m).replace('\\','/') or str(m).endswith('/static'):
                        preferred = m
                        break
                located = preferred or matches[0]

        if not located:
            missing.append(rr)
        else:
            found.append((rr, str(located)))
    return found, missing


if __name__ == '__main__':
    bootstrap_django()

    # scan the whole project for CSS and HTML files (excluding venv/staticfiles)
    project_root = Path(__file__).resolve().parents[1]
    all_refs = find_static_references(project_root)

    print(f'Found {len(all_refs)} static references to check')
    found, missing = check_refs(all_refs)

    if found:
        print('\nSample found references (first 20):')
        for k, v in found[:20]:
            print('  ', k, '->', v)

    if missing:
        print('\nMissing static references:')
        for m in missing:
            print('  ', m)
        print('\nThese missing references can cause ManifestStaticFilesStorage errors during collectstatic.')
        sys.exit(2)
    else:
        print('\nAll references resolved by staticfiles finders.')
        sys.exit(0)
