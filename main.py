 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 11:29:22 2022

@author: 19761378
"""

from flask import Flask, render_template, request, jsonify 
from backend import get_session, get_add_data, get_bboxed_data, from_db_to_dict_bbox, get_full_mood, send_mood_map
import json
import logging
from functools import wraps
from urllib.parse import unquote

#logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def logging_isempty(text, data, path):
    if data:
        logging.debug(text, data, ' from ', path)
    else:
        logging.error('No data from ', path)
       

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['JSON_AS_ASCII'] = False

session = get_session()

logging.info('Started application and received DB session')

def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            resp = func(*args, **kwargs)
            resp.set_data('{}({})'.format(
                str(callback),
                resp.get_data(as_text=True)
            ))
            resp.mimetype = 'application/javascript'
            return resp
        else:
            return func(*args, **kwargs)
    return decorated_function

#открывает главную страничку с картой. 
@app.route('/', methods = ['POST', 'GET'])
def index():
    logging.info('Rendering homepage')
    return render_template('map_page.html')

#загружает страничку с тепловой картой
@app.route('/heatmap', methods = ['POST', 'GET'])
def heat():
    logging.info('Rendering heatmap')
    return render_template('teplokarta.html')

#получает запрос на данные от тепловой карты и отдает файл
@app.route('/heatmap/getdata', methods = ['POST', 'GET'])
def getheat():
    starttime=request.args.get('tstart')
    finishtime=request.args.get('tfinish')
    logging.info('received_request',starttime, finishtime)
    if (starttime and finishtime):
        mood_to_process = get_full_mood(session, starttime, finishtime)
    else:
        mood_to_process = get_full_mood(session)
    data = send_mood_map(session, mood_to_process)
    return jsonify(data)
                         
#загружает дополнительные данные по заявке и закидывает в карту в виде json 
@app.route("/load_additional_data", methods=['GET', 'POST'])
def add_data():
    ids = request.get_json()
    logging.debug('Received request for additional data, ids= ', ids)

    out = get_add_data(session, ids)

    logging_isempty('Loaded additional data from DB:', out, 'DB')   
    return json.dumps(out)

#открывает страницу о команде
@app.route('/about')
def about():
    logging.info('Rendering about page')
    return render_template("about.html")



#отдает в карту инфу по меткам в запрошенной картой области
@app.route('/getGeoObject/tile', methods = ['GET', 'POST'])
@jsonp
def getGeoObject():
    starttime=request.args.get('start_time')
    finishtime=request.args.get('finish_time')
    problems=request.args.get('problems').split(',')
    
    try:
        searchline=unquote(request.args.get('problemnum'))
    except:
        searchline=None
        logging.debug("No search query or incorrect format")
    try:
        is_problem = (request.args.get('isproblem'))  
    except:
        is_problem = 'all'
     
    tile = request.args.get('bbox')
    bbox = tile.split(sep=',')
    logging.debug('Received request for data in bbox and dates', bbox, problems, starttime, finishtime, searchline, is_problem)
        
    items = get_bboxed_data(session, bbox, problems, starttime, finishtime, searchline, is_problem)
    marks = from_db_to_dict_bbox(session, items)
    logging.info(marks)    
    return jsonify(marks)
   

#открывает страничку данных команды
@app.route('/contact', methods = ['GET'])
def contact():
    return render_template('contact.html')


if __name__ == "__main__":
    session = get_session()
    app.run(debug=False)   
    
