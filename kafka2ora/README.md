# Kafka2ora
通过消费Kafka将CNC设备信息存入数据库

## 1.程序运行 

```
 python kafka2ora.py    
```

## 2.程序结构及说明

kafkaclient.py-------------------------实现kafka生产者及消费者功能

kafka2ora.py--------------------------通过使用kafkaclient，把kafka数据                        存入数据库

database.py---------------------------封装了数据库的基本操作

cncparsing.py-------------------------解析数据，根据数据生成不同的SQL语句，并将数据存入数据库

config.yaml-----------------------------程序配置文件

## 3.Python运行依赖库

- pip install cx_Oracle
- pip install pykafka
- pip install pyyaml