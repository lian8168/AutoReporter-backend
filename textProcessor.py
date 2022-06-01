import Database
from common import *
from tqdm import tqdm
from NerProcessor import Ner
import json


def create_word_dict_txt(db):
    texts = db.get_seqs_from_dates('20200501', '20220520')
    with open('word_dict.txt', 'w', encoding='UTF-8') as word_f:
        for text in texts:
            word_f.writelines(text)
            word_f.writelines('\n')
    word_f.close()


def create_user_dict_txt():
    with open('./cache/env/20200501_20220520.json', 'r', encoding='UTF-8') as cache_file:
        cache_text = json.load(cache_file)
    cache_file.close()
    with open('user_dict1.txt', 'w', encoding='UTF-8') as fOut:
        for item in cache_text['text']:
            fOut.writelines(item['env'])
            fOut.writelines('\n')
    fOut.close()


class TextProcessor:
    def __init__(self, checkpoint_save_path, entity_labels, max_len, lstm_units, drop_rate, leraning_rate, epsilon,
                 lamb):
        self.db = Database.Database()
        self.nerProcessor = Ner(checkpoint_save_path, entity_labels, max_len, lstm_units, drop_rate, leraning_rate,
                                epsilon, lamb)

    def get_text_between_dates(self, start_date, end_date, cache_dir):
        # has_cache = False
        # for root, dirs, files in os.walk('./cache', topdown=True):
        #     for file in files:
        #         dates = file.split('.')[0].split('_')
        #         s_date, e_date = dates[0], dates[1]
        #         if s_date == start_date and e_date == end_date:
        #             has_cache = True
        #             with open(os.path.join(root, file), 'r', encoding='UTF-8') as cache_file:
        #                 cache_text = json.load(cache_file)
        #             cache_file.close()
        #             break
        # if has_cache:
        #     return cache_text
        texts = self.db.get_seqs_from_dates(start_date, end_date)
        pred_seqs = []
        seqs = {}
        list = []
        num = 1
        total = len(texts)
        for text in texts:
            print(str(num) + '/' + str(total))
            num += 1
            pred = self.nerProcessor.perdict(text[0])
            if len(pred) > 0:
                tem_doc = []
                for p in pred:
                    tem_doc.append(p[0])
                    if seqs.get(p[0]) is None:
                        seqs[p[0]] = 1
                    else:
                        seqs[p[0]] += 1
                pred_seqs.append(tem_doc)
        for key in seqs:
            tem = {}
            tem['env'] = key
            tem['val'] = seqs[key]
            list.append(tem)
        env_dict = {}
        env_dict['text'] = list
        env_dict['total'] = total
        filename = str(start_date) + '_' + str(end_date) + '.json'
        file_path = os.path.join(cache_dir, filename)
        with open(file_path, 'w', encoding='UTF-8') as out_f:
            json.dump(env_dict, out_f, ensure_ascii=False)
        out_f.close()
        with open('lda_text', 'w', encoding='UTF-8') as lda_f:
            json.dump(pred_seqs, lda_f, ensure_ascii=False)
        lda_f.close()
        return env_dict

    def eval_all_input(self, texts):
        pred_seqs = []
        seqs = {}
        list = []
        num = 1
        total = len(texts)
        for text in tqdm(texts):
            # print(str(num) + '/' + str(total))
            num += 1
            pred = self.nerProcessor.perdict(text[0])
            if len(pred) > 0:
                tem_doc = []
                for p in pred:
                    tem_doc.append(p[0])
                    if seqs.get(p[0]) is None:
                        seqs[p[0]] = 1
                    else:
                        seqs[p[0]] += 1
                pred_seqs.append(tem_doc)
        for key in seqs:
            tem = {}
            tem['env'] = key
            tem['val'] = seqs[key]
            list.append(tem)
        env_dict = {}
        env_dict['text'] = list
        env_dict['total'] = total
        with open('lda_text', 'w', encoding='UTF-8') as lda_f:
            json.dump(pred_seqs, lda_f, ensure_ascii=False)
        lda_f.close()
        return env_dict


if __name__ == '__main__':
    texts = []
    with open("C:/Users/lyc/Desktop/导航迷路.txt", 'r', encoding='UTF-8') as file:
        for line in file.readlines():
            texts.append(line.split('\n')[0])
    file.close()
    text_processor = TextProcessor('./checkpoint/env', ['ENV'], 256, 512, 0.005, 5e-5, 0.5, 1000)
    text_processor.eval_all_input(texts)
