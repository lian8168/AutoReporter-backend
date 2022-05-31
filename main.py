from flask import Flask, request
from flask import jsonify
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from common import *
from myConfig import *

# 全局变量，多线程共享
app = Flask(__name__)
CORS(app, supports_credentials=True, resources=r'/*')


# @app.before_request
# def before_request():
#     if request.url.startswith('http://'):
#         url = request.url.replace('http://', 'https://', 1)
#         return redirect(url, code=301)


@app.route('/env', methods=['POST', 'GET'])
def get_text():  # 编码OK， 接口OK
    data = request.get_json()
    start_date = data['start_date'].replace('-', '')
    end_date = data['end_date'].replace('-', '')
    print(start_date, end_date)
    has_cache, cache_text = test_cache_env(start_date, end_date, './cache/env')
    if has_cache:
        text = cache_text
    else:
        env_text_processor = TextProcessor(env_checkpoint_path, env_labels, env_max_len, env_lstm_units, env_drop_rate,
                                           env_leraning_rate, env_epsilon, env_lamb)
        text = env_text_processor.get_text_between_dates(start_date, end_date, './cache/env')
    return jsonify(text)


@app.route('/loc', methods=['POST', 'GET'])
def get_loc_without_city():
    data = request.get_json()
    start_date = data['start_date'].replace('-', '')
    end_date = data['end_date'].replace('-', '')
    _, loc_without_city = get_city(start_date, end_date)
    return jsonify(loc_without_city)


@app.route('/city', methods=['POST', 'GET'])
def get_loc_city():
    # data = request.get_json()
    # start_date = data['start_date'].replace('-', '')
    # end_date = data['end_date'].replace('-', '')
    start_date = '20200501'
    end_date = '20220511'
    province_city, _ = get_city(start_date, end_date)
    return jsonify(province_city)


# def get_loc():  # 编码OK， 接口OK
#     data = request.get_json()
#     start_date = data['start_date'].replace('-', '')
#     end_date = data['end_date'].replace('-', '')
#     print(start_date, end_date)
#     has_cache, cache_text = test_cache_env(start_date, end_date, './cache/loc')
#     if has_cache:
#         text = cache_text
#     else:
#         text_processor = TextProcessor('./checkpoint/loc', ['LOC'], 256, 0.0002, 9e-5)
#         text = text_processor.get_text_between_dates(start_date, end_date, './cache/loc')
#     return jsonify(text)


# @app.route('/env',  methods=['POST', 'GET'])
# def get_text_from_cache():  # 编码OK， 接口OK
#     data = request.form
#     start_date = data['start_date']
#     end_date = data['end_date']
#     for root, dirs, files in os.walk('./cache', topdown=True):
#         for file in files:
#             dates = file.split('.')[0].split('_')
#             s_date, e_date = dates[0], dates[1]
#             if s_date == start_date and e_date == end_date:
#                 with open(os.path.join(root, file), 'r', encoding='UTF-8') as cache_file:
#                     text = json.load(cache_file)
#     response = {
#         'text': text,
#     }
#     return jsonify(response)


if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()
