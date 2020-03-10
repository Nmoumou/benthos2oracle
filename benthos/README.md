# Benthos
此版本为windows版，其他方式请参看官网https://www.benthos.dev/

## 运行方式

```bash
benthos -c config.yaml
```

## 配置文件功能

1.接收MQTT信息并将信息写入Kafka中

2.处理MQTT原始信息（JSON格式），并在信息中添加主题topic字段