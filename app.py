import base64
import glob
import json
import os
import sys

from PIL import Image
from io import BytesIO
from logic import Annotation

IMAGE_FOLDER = sys.argv[1]
try:
    with open(sys.argv[2]) as f:
        heuristics = json.load(f)
except:
    heuristics = None
ann = Annotation(os.listdir(IMAGE_FOLDER), heuristics)
contribution = {}

from flask import Flask, render_template, redirect, url_for, request, make_response

app = Flask(__name__, template_folder='./templates')
app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER


@app.route('/', methods=['POST', 'GET'])
def home():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    name = request.form.get('username')
    contribution[name] = 0
    resp = make_response(redirect(url_for('annotator')))
    resp.set_cookie('username', name)
    return resp


@app.route('/annotator', methods=['POST', 'GET'])
def annotator():
    username = request.cookies.get('username')
    done = contribution[username]
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
    folder = os.path.join(IMAGE_FOLDER, name, '*.jpg')
    img_lst = []
    width = height = 0
    width_lst = []
    for p in glob.glob(folder):
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


@app.route('/submit', methods=['POST'])
def submit():
    username = request.cookies.get('username')
    contribution[username] += 1
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


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
