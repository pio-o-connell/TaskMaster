# Heroku setup helper (PowerShell)
# Usage: Edit $appName then run in your local shell where `heroku` CLI is installed and you're auth'd.

param(
    [string]$appName = ''
)

if (-not $appName) {
    Write-Host "Please supply an app name: .\heroku_setup.ps1 -appName 'my-app-name'"
    exit 1
}

Write-Host "Creating Heroku app: $appName"
heroku create $appName

Write-Host "Adding Postgres addon"
heroku addons:create heroku-postgresql:hobby-dev --app $appName

Write-Host "Set required config vars (run the generate_secret script to create SECRET_KEY)"
$secret = Read-Host -Prompt 'Paste SECRET_KEY (generated using scripts/generate_secret.py)'

Write-Host "Setting HEROKU config vars"
heroku config:set SECRET_KEY=$secret DEBUG=False ALLOWED_HOSTS=$appName.herokuapp.com --app $appName

Write-Host "Pushing to Heroku (ensure changes committed)"
Write-Host "git push heroku main"

Write-Host "After push, run migrations and collectstatic on Heroku:" 
Write-Host "heroku run python manage.py migrate --app $appName"
Write-Host "heroku run python manage.py collectstatic --noinput --app $appName"

Write-Host "Done. Use 'heroku logs --tail --app $appName' to monitor runtime logs."
