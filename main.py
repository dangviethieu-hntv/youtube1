# -*- coding: utf-8 -*-  
from flask import Flask, render_template, json, request, send_file,request, flash, redirect
import handleCrawl
import os

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/search', methods=['POST','GET'])
def result():
    keyword = request.args.get('k', default = '', type = str)
    page = request.args.get('page', default ='1', type = str)
    return json.dumps(handleCrawl.crawlSearch(keyword, page))

@app.route('/video/<uid>', methods=['POST','GET'])
def video(uid):
    return json.dumps(handleCrawl.crawlWatch(uid))

@app.route('/channel/<uid>', methods=['POST','GET'])
def channel(uid):
    return json.dumps(handleCrawl.crawlChannel(uid))

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(debug=True, port=port, host='0.0.0.0')
