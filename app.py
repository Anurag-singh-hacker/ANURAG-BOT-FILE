from flask import Flask, jsonify, send_file
import json, os

app = Flask(__name__)
DATA_FILE = "data.json"

def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"folders": {}, "recent": []}

@app.route("/data")
def data():
    return jsonify(load())

@app.route("/")
def panel():
    return send_file("index.html")

if __name__ == "__main__":
    app.run(port=5000, debug=True)