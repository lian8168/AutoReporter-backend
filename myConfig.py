import configparser

conf = configparser.ConfigParser()
conf.read("config.ini")

host = conf.get("mysql", "host")
user = conf.get("mysql", "user")
password = conf.get("mysql", "password")
database = conf.get("mysql", "database")

loc_checkpoint_path = conf.get("ner_loc", "checkpoint_save_path")
loc_labels = list(conf.get("ner_loc", "entity_labels"))
loc_max_len = int(conf.get("ner_loc", "max_len"))
loc_lstm_units = int(conf.get("ner_loc", "lstm_units"))
loc_drop_rate = float(conf.get("ner_loc", "drop_rate"))
loc_leraning_rate = float(conf.get("ner_loc", "leraning_rate"))
loc_epsilon = float(conf.get("ner_loc", "epsilon"))
loc_lamb = int(conf.get("ner_loc", "lamb"))

env_checkpoint_path = conf.get("ner_env", "checkpoint_save_path")
env_labels = list(conf.get("ner_env", "entity_labels"))
env_max_len = int(conf.get("ner_env", "max_len"))
env_lstm_units = int(conf.get("ner_env", "lstm_units"))
env_drop_rate = float(conf.get("ner_env", "drop_rate"))
env_leraning_rate = float(conf.get("ner_env", "leraning_rate"))
env_epsilon = float(conf.get("ner_env", "epsilon"))
env_lamb = int(conf.get("ner_env", "lamb"))








# 数据库配置文件