import MySQLdb
from myConfig import *


class Database:
    def __init__(self):
        # self.IP = "localhost"
        # self.username = "root"  # 数据库用户
        # self.password = "123456"  # 数据库用户密码
        # self.database = "automind"  # 数据库名
        self.IP = host
        self.username = user
        self.password = password
        self.database = database
        self.db = MySQLdb.connect(host=self.IP, user=self.username, passwd=self.password, db=self.database,
                                  charset='utf8')
        self.cursor = self.db.cursor()

    # 查询指定日期范围内的文本
    def get_seqs_from_dates(self, start_date, end_date):
        sql = f"select text from weibo where DATE_FORMAT(created_at,'%Y%m%d') between '{start_date}' and '{end_date}'"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return results

# 这个是数据库操作的类
