from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def dashboard():
    city = request.args.get("city","").strip()
    error = ""
    temperature = 26

    if "city" in request.args and city == "":

        error = "please enter a valid City Name"
    
    return render_template("index.html",city=city,temperature=temperature, error = error)