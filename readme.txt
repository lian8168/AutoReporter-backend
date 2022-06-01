##后端


####依赖
requirements.txt中

# 注：MySQLdb包的依赖是python3的mysqlclient而不是python2的MySQL-python

####目录结构
cache为缓存目录
checkpoint为ner模型检查点目录
cities.py为城市抽取类
Database.py为封装的数据库类
common.py为基本方法函数
myConfig.py为读取config.ini的变量定义
NerProcessor.py为封装的ner类
textProcessor.py为封装的利用ner识别文本类
main.py为入口函数

config.ini中包含着数据库与ner模型检查点路径和超参数配置

####运行
1.安装依赖
pip install -r requirements.txt
2.导入数据
将weibo.sql导入至自己的mysql数据库中
3.配置
config.ini中进行相关的配置
4.运行main.py



