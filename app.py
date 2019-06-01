import argparse
import json
import logging
import os
from pathlib import Path

from flask import abort, Flask, redirect, render_template, request, Response

app = Flask(__name__)


def scan_next(file=None):
    try:
        i = app.sequence.index(file) + 1
    except ValueError:
        i = 0
    while i < len(app.sequence) and not (app.dirname / app.sequence[i]).is_file():
        i += 1
    if i >= len(app.sequence):
        raise StopIteration
    return app.sequence[i]


def scan_previous(file=None):
    try:
        i = app.sequence.index(file) - 1
    except ValueError:
        i = 0
    while i >= 0 and not (app.dirname / app.sequence[i]).is_file():
        i -= 1
    if i < 0:
        raise StopIteration(file)
    return app.sequence[i]


def load_labels(file: str) -> dict:
    fp = Path(file)
    labels_file = (app.dirname / "json" / fp.name).with_suffix(".json")
    try:
        with open(labels_file) as fin:
            return json.load(fin)
    except IOError:
        return {}


def write_labels(file: str, data: dict):
    fp = Path(file)
    labels_file = (app.dirname / "json" / fp.name).with_suffix(".json")
    with open(labels_file, "w") as fout:
        return json.dump(data, fout)


@app.route("/")
def root():
    try:
        file = scan_next()
        while load_labels(file):
            file = scan_next(file)
        return redirect("/" + file)
    except StopIteration:
        abort(404)


@app.route("/<file>")
def ui(file):
    if file == "favicon.ico":
        abort(404)
    try:
        next_file = scan_next(file)
    except StopIteration:
        next_file = ""
    try:
        previous_file = scan_previous(file)
    except StopIteration:
        previous_file = ""
    return render_template("ui.html", image=file, index=app.sequence.index(file) + 1,
                           total=len(app.sequence), labels=app.labels, checked=load_labels(file),
                           next_image=next_file, previous_image=previous_file)


@app.route("/img/<file>")
def image(file):
    return Response(open(app.dirname / file, "rb"))


@app.route("/label/<file>", methods=["PUT"])
def label(file):
    write_labels(file, request.json)
    return "", 204


@app.route("/robots.txt")
def robots():
    abort(404)


def run():
    app.logger.setLevel(logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", default=8080, type=int)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--labels", required=True, help="Path to the file with labels")
    parser.add_argument("--images", required=True, help="Path to the directory with images")
    args = parser.parse_args()
    with open(args.labels) as fin:
        app.labels = [l.split("#")[0].strip().lower() for l in fin]
    app.sequence = sorted(os.listdir(args.images))
    app.logger.info("Enumerated %d files", len(app.sequence))
    app.dirname = Path(args.images)
    (app.dirname / "json").mkdir(exist_ok=True)
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    run()
