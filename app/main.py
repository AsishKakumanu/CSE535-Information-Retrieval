from flask import Flask, render_template

app = Flask(__name__,static_url_path='/static')

@app.route('/')
def home():
    return render_template('main.html')

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATE_AUTO_RELOAD'] = True
    app.run(debug=True)

