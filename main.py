from flask import Flask, render_template, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from wordcloud import WordCloud
from bs4 import BeautifulSoup
import requests

LOCATIONS = {
    "philly":"http://foodpro.unh.edu/shortmenu.asp?sName=University%20Of%20New%20Hampshire%20Hospitality%20Services&locationNum=30&locationName=Philbrook%20Dining%20Hall&naFlag=1",
    "hoco":"http://foodpro.unh.edu/shortmenu.asp?sName=University%20Of%20New%20Hampshire%20Hospitality%20Services&locationNum=80&locationName=Holloway%20Dining%20Hall&naFlag=1"
}

# Flask webserver
app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address)
CORS(app)

# Main Page
@app.route("/")
def index():
    return render_template("./index.html"), 200

@app.route("/generate", methods=["POST"])
@limiter.limit("1/second;15/minute")
def generate():
    
    # Sample Menu (3/10/22)
    params = request.get_json()
    if params.get("location") == "sample":
        with open("static/sample.txt") as file:
            words = file.read().splitlines()
    
    # Live Menu
    elif params.get("location") not in LOCATIONS:
        return {"error":"Invalid location"}, 400

    else:
        words = []
        req = requests.get(LOCATIONS.get(params["location"]))
        if not req.status_code == 200: return {"error":"Couln't get menu."}, 400
        for item in BeautifulSoup(req.content, "html.parser").find_all(class_="shortmenurecipes"):
            for word in item.text.split():
                words.append(word)

    if not words: return {"error":"No menu today, try \"Sample\" location."}, 400
    wordcloud = WordCloud(
        width=1080,
        height=720,
        background_color=params.get("color") or "white",
        min_font_size=10
    ).generate(" ".join(words))
    return {"generated":wordcloud.to_svg()}, 200

@app.errorhandler(400)
def bad_request(*_):
    return {"error":"Bad request."}, 400
    
@app.errorhandler(404)
def not_found(*_):
    return render_template("./404.html"), 404

@app.errorhandler(405)
def method_not_allowed(*_):
    return {"error":"Method not allowed."}, 405
    
@app.errorhandler(429)
def rate_limit(*_):
    return {"error":"You're doing that too fast!"}, 429

if __name__ == "__main__":
    app.run()
