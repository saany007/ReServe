from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)


app.wsgi_app = ProxyFix(app.wsgi_app)

@app.route('/')
def home():
    return render_template('index.html')  # Make sure this exists in /templates


def handler(environ, start_response):
    return app(environ, start_response)