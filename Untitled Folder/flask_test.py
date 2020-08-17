from flask import Flask, render_template

app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("layout.html")
@app.route("/test")
def test():
    return "<h1 style='color: lightblue;'> TEST</h1>"










if __name__ == "__main__":
    app.run(debug=True)

