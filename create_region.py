import json

def create():
    with open('./cities.json', 'r', encoding='UTF-8') as city_f:
        city_dict = json.load(city_f)
    city_f.close()
    value = 1
    cities = []
    for item in city_dict["provinces"]:
        tem_dict = {}
        tem_dict["value"] = value
        tem_dict["label"] = item["provinceName"]
        tem_dict["children"] = []
        for city in item["citys"]:
            value += 1
            tem_city_dict = {}
            tem_city_dict["value"] = value
            tem_city_dict["label"] = city["citysName"]
            tem_dict["children"].append(tem_city_dict)
        value += 1
        cities.append(tem_dict)
    return cities

def out_put(dict):
    with open("citylist.json", 'w', encoding='UTF-8') as out_f:
        json.dump(dict, out_f, ensure_ascii=False)
    out_f.close()

if __name__ == '__main__':
    dict = create()
    out_put(dict)
