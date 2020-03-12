import yaml
import json
import logger
import traceback
from cncparsing import CNCParsing
from kafkaclient import CncKafka
        

if __name__ == "__main__":
    try:
        # 初始化Kafka
        kclient = CncKafka()
        consumer  = kclient.getconsumer()
        cncparse = CNCParsing()
        for message in consumer:
            # 解析并存入Oracle数据
            kmsg = message.value.decode('utf-8')
            resmsg =json.loads(kmsg)
            try:
                cncparse.parse(resmsg['topic'], resmsg)
            except:
                errstr = traceback.format_exc()
                logger.writeLog("Kafka消费数据写入库错误:" + errstr + kmsg , "kafka2ora.log")

    except:
        errstr = traceback.format_exc()
        logger.writeLog("Kafka消费数据写入库错误:" + errstr, "kafka2ora.log")