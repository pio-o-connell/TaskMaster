from django.http import HttpResponse


def index(request):
    html = """
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>The install worked successfully</title>
        <style>body{font-family:Helvetica,Arial,sans-serif;margin:40px}</style>
      </head>
      <body>
        <h1>It worked!</h1>
        <p>The install worked successfully! Congratulations!</p>
      </body>
    </html>
    """
    return HttpResponse(html)
