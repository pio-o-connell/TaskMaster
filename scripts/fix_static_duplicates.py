#!/usr/bin/env python3
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
# Ensure project root on path and settings available
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmaster.settings')

try:
    import django
    django.setup()
    from django.contrib.staticfiles import finders
except Exception as e:
    print('Failed to bootstrap Django:', e)
    sys.exit(1)

TARGET = 'css/style.css'
paths = list(finders.find(TARGET, all=True))
print('Found paths for', TARGET, ':')
for p in paths:
    print(' -', p)

# Keep any path that is inside tasks/static; remove others
app_static_dir = str(ROOT / 'tasks' / 'static')
removed = []
for p in paths:
    if app_static_dir in str(Path(p)):
        print('Keeping app static copy:', p)
    else:
        try:
            print('Removing duplicate static file:', p)
            os.remove(p)
            removed.append(p)
        except Exception as exc:
            print('Failed to remove', p, exc)

print('Removed files:', removed)
print('Done')
