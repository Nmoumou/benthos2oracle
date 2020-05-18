import yaml
import logger
import json
from kafka import KafkaConsumer
import traceback
import time


class CncKafka:
    kafkahosts = None
    kafkatopic = None
    consumergroup = None
    consumerid = None
    kafkaclient = None
    producer = None

    def __init__(self):
        '''
        初始化，从配置文件读取服务器信息
        '''
        try:
            f = open("config.yaml","r+",encoding="utf-8")
            fstream = f.read()
            configobj = yaml.safe_load(fstream)
            self.kafkahosts = configobj['kafka']['server']
            self.kafkatopic = configobj['kafka']['topic']
            self.consumergroup = configobj['kafka']['consumergroup']
            self.consumerid = configobj['kafka']['consumerid']
        except:
            errstr = traceback.format_exc()
            logger.writeLog("Kafka客户端读取配置信息失败:" + errstr, "kafka.log")

    def getconsumer(self):
        '''
        返回一个消费者对象
        '''
        try:
            # 消费最新的消息，并且自动提交偏移
            consumer = KafkaConsumer(self.kafkatopic,
                         group_id=self.consumergroup,
                         client_id=self.consumerid,
                         bootstrap_servers=self.kafkahosts,
                         auto_offset_reset = 'earliest')
            logger.writeLog("Kafka消费者初始化成功", "kafka.log")
            return consumer
        except:
            errstr = traceback.format_exc()
            logger.writeLog("Kafka消费者实例化失败:" + errstr, "kafka.log")