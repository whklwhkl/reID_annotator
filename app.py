import argparse
import base64
import glob
import json
import os
import sys

from PIL import Image
from flask import Flask, render_template, redirect, url_for, request, make_response
from functools import wraps
from io import BytesIO
from logic import Annotation

ap = argparse.ArgumentParser()
ap.add_argument('folder', help='path of the image folder, where each subfolder\'s name is the respective label name')
ap.add_argument('--order', '-o', default=None, help='[optional]path to the json file that holds a list of pairs of labels')
ap.add_argument('--port', '-p', default=5000, type=int, help='port number for http requests')
ap.add_argument('--debug', action='store_true', help='debug mode')
args = ap.parse_args()

if args.order is not None:
    with open(args.order) as f:
        order = json.load(f)
else:
    order = None

ann = Annotation(os.listdir(args.folder), order)
contribution = {}

app = Flask(__name__, template_folder='./templates')
app.config['UPLOAD_FOLDER'] = args.folder


@app.route('/', methods=['POST', 'GET'])
def home():
    username = request.cookies.get('username')
    if username in contribution:
        return redirect(url_for('annotator'))
    else:
        return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    name = request.form.get('username')
    if name not in contribution:
        contribution[name] = 0
    resp = make_response(redirect(url_for('annotator')))
    resp.set_cookie('username', name)
    return resp


def require_user(fn):
    @wraps(fn)
    def wrapped():
        username = request.cookies.get('username')
        try:
            done = contribution[username]
        except KeyError:
            return render_template('login.html')
        return fn(username, done)
    return wrapped


@app.route('/annotator', methods=['POST', 'GET'])
@require_user
def annotator(username, done):
    try:
        n1, n2 = ann.new_job()
    except TypeError:
        return f'Well done, {username}!<br>You have completed {done} pairs!<br><a href="/download">download</a>'
    return render_template('annotator.html',
                           done=done,
                           max=ann.max_step,
                           user=username,
                           name1=n1.name, name2=n2.name,
                           image1=image_html(n1.name), image2=image_html(n2.name))


def image_html(name):
    folder = os.path.join(args.folder, name, '*.*')
    img_lst = []
    width = height = 0
    width_lst = []
    for p in glob.glob(folder):
        if p.endswith(('.jpg', '.png', '.JPG', '.PNG')):
            img = Image.open(p)
            w, h = img.size
            width_lst.append(width)
            width += w
            height = max(height, h)
            img_lst.append(Image.open(p))
    new_img = Image.new('RGB', [width, height])
    for i, w in zip(img_lst, width_lst):
        new_img.paste(i, [w, 0])
    imb = BytesIO()
    new_img.save(imb, format='PNG')
    ims = base64.b64encode(imb.getvalue()).decode('utf-8')
    return ims


@app.route('/ignore', methods=['POST', 'GET'])
@require_user
def ignore(username, done):
    contribution[username] = 1 + done
    name = request.args.get('name')
    ann.ignore(name)
    return redirect(url_for('annotator'))


@app.route('/submit', methods=['POST'])
@require_user
def submit(username, done):
    contribution[username] = 1 + done
    name1 = request.form.get('name1')
    name2 = request.form.get('name2')
    case = request.form.get('submit')
    if case == 'yes':
        ann.submit(True, name1, name2)
    elif case == 'no':
        ann.submit(False, name1, name2)
    return redirect(url_for('annotator'))


@app.route('/download')
def download():
    return json.dumps({n.name:[m.name for m in n if m.name != n.name] for n in ann.visited}, indent=2)


@app.route('/upload', methods=['POST'])
def upload():
    record = request.files.get('record')
    if record:
        record = json.loads(record.read())
        for name1, names in record.items():
            for name2 in names:
                ann.submit(True, name1, name2)
    return f'uploaded\n'


@app.route('/contributor')
def contributor():
    page = '<table border="1"><tr><th>NAME</th><th>ANNOTATED</th></tr>{}</table>'
    table = ''
    for k, v in contribution.items():
        table += f'<tr> <td>{k}</td> <td>{v}</td> </tr>'
    return page.format(table)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=args.port, debug=args.debug)
