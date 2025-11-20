"""Generate a Django SECRET_KEY suitable for production.

Usage:
    python scripts/generate_secret.py

This prints a random 50+ char string you can copy to Heroku config vars.
"""
import secrets
import string

ALPHABET = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"

def generate_secret(length=50):
    return ''.join(secrets.choice(ALPHABET) for _ in range(length))

if __name__ == '__main__':
    print(generate_secret(64))
