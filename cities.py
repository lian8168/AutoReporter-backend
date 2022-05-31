import json


class Cities:
    def __init__(self):
        self.city_list = []
        self.city_file_path = './cities.json'

    def read_city_list(self):
        with open(self.city_file_path, 'r', encoding='UTF-8') as load_f:
            load_city = json.load(load_f)
            self.city_list = load_city['provinces']
        load_f.close()

    def province_from_city(self, city_name):
        province = ''
        res_city = ''
        for city in self.city_list:
            for c_name in city['citys']:
                if c_name['citysName'].find(city_name) != -1:
                    province = city['provinceName']
                    res_city = c_name['citysName']
                    return province, res_city
        return 'null', 'null'

    def create_geojson(self, province_dict, city_dict):
        with open('./provinces.json', 'r', encoding='UTF-8') as pro_f:
            provinces = json.load(pro_f)
        pro_f.close()
        with open('./citydata.json', 'r', encoding='UTF-8') as city_f:
            city_data = json.load(city_f)
        city_f.close()
        for province in province_dict:
            for p_name in provinces:
                if province == p_name["name"]:
                    p_name["次数"] = province_dict[province]
        res_province = sorted(provinces, key=lambda e: e["次数"], reverse=True)
        level = 1
        for res_p in res_province:
            if res_p["次数"] > 0:
                res_p["排名"] = level
                level += 1
            else:
                res_p["排名"] = level
        return res_province

    def create_geo_city_json(self, city_dict):
        with open('./citydata.json', 'r', encoding='UTF-8') as city_f:
            city_data = json.load(city_f)
        city_f.close()
        for city_name in city_dict:
            for c_data in city_data:
                if city_name == c_data["name"]:
                    c_data["次数"] = city_dict[city_name]
        res_city = sorted(city_data, key=lambda e: e["次数"], reverse=True)
        level = 1
        current = res_city[0]["次数"]
        next_add = 0
        for res_c in res_city:
            if res_c["次数"] > 0:
                if current == res_c["次数"]:
                    next_add += 1
                else:
                    level += next_add
                    next_add = 1
                current = res_c["次数"]
                res_c["排名"] = level
            else:
                level += next_add
                next_add = 0
                res_c["排名"] = level
        return res_city



if __name__ == '__main__':
    cities = Cities()
    cities.read_city_list()
    province, city = cities.province_from_city('重庆')
    province_dict = {}
    city_dict = {}
    province_dict["北京市"] = 5
    province_dict["重庆市"] = 10
    province_dict["深圳市"] = 10
    province_dict["商丘市"] = 5
    province_dict["厦门市"] = 45
    res = cities.create_geo_city_json(province_dict)
    print(res)
    print(province, city)
