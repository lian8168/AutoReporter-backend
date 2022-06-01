import os
from textProcessor import *
from cities import *
from myConfig import *


def test_cache_env(start_date, end_date, cache_dir):
    has_cache = False
    cache_text = ''
    total = 0
    for root, dirs, files in os.walk(cache_dir, topdown=True):
        for file in files:
            dates = file.split('.')[0].split('_')
            s_date, e_date = dates[0], dates[1]
            if s_date == start_date and e_date == end_date:
                has_cache = True
                with open(os.path.join(root, file), 'r', encoding='UTF-8') as cache_file:
                    cache_text = json.load(cache_file)
                cache_file.close()
                break
    return has_cache, cache_text


def get_loc(start_date, end_date):
    has_cache, cache_text = test_cache_env(start_date, end_date, './cache/loc')
    if has_cache:
        text = cache_text
    else:
        loc_text_processor = TextProcessor(loc_checkpoint_path, loc_labels, loc_max_len, loc_lstm_units, loc_drop_rate,
                                           loc_leraning_rate, loc_epsilon, loc_lamb)
        text = loc_text_processor.get_text_between_dates(start_date, end_date, './cache/loc')
    return text


def get_city(start_date, end_date):
    text = get_loc(start_date, end_date)
    cities = Cities()
    cities.read_city_list()
    province_city_list = []
    other_loc = []
    provinces_dict = {}
    cities_dict = {}
    for item in text["text"]:
        tem_province, tem_city = cities.province_from_city(item["env"])
        if tem_city != 'null':
            if cities_dict.get(tem_city) is not None:
                cities_dict[tem_city] += item["val"]
            else:
                cities_dict[tem_city] = item["val"]
            # if provinces_dict.get(tem_province) is None:
            #     provinces_dict[tem_province] = 1
            # else:
            #     provinces_dict[tem_province] += 1
            # if cities_dict.get(tem_city) is None:
            #     cities_dict[tem_city] = 1
            # else:
            #     cities_dict[tem_city] += 1
            tem_dic = {}
            tem_dic['province'] = tem_province
            tem_dic['city'] = tem_city
            tem_dic['val'] = item["val"]
            province_city_list.append(tem_dic)
        else:
            other_loc.append(item)
    res_city = cities.create_geo_city_json(cities_dict)
    province_city_dict = {}
    other_loc_dict = {}
    province_city_dict["text"] = province_city_list
    province_city_dict["total"] = text["total"]
    other_loc_dict["text"] = other_loc
    other_loc_dict["total"] = text["total"]
    return res_city, other_loc_dict


def write_loc_without_city():
    _, loc_without_city = get_city('20200501', '20220511')
    loc_file = open('loc_with_city.txt', 'w', encoding='UTF-8')
    for loc in loc_without_city["text"]:
        loc_file.writelines(loc["env"])
        loc_file.writelines('\n')
    loc_file.close()
