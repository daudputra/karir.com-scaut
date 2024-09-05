# from kafka import KafkaProducer
# import json

# from src.helper.mylog import log_message

# class Producer:
#     def __init__(self, bootstrap_server: list) -> None:
#         self.producer = KafkaProducer(bootstrap_servers=bootstrap_server)
    
#     def send(self, topic, data: dict):
#         try:
#             log_message('DEBUG', 'logs/debug.log', f"trying send to kafka topic: {topic}")
#             self.producer.send(topic, str.encode(json.dumps(data)))
#             log_message('INFO', 'logs/kafka_info.log', "Terkirim ke kafka " + json.dumps(data))
#         except Exception as e:
#             log_message('ERROR', 'logs/error.log', f"error when trying send to kafka: {e}")

from confluent_kafka import Producer as ConfluentProducer
import json
from src.helper.mylog import log_message

class Producer:
    def __init__(self, bootstrap_servers: list) -> None:
        conf = {'bootstrap.servers': ','.join(bootstrap_servers)}
        self.producer = ConfluentProducer(conf)
    
    def send(self, topic, data: dict):
        try:
            log_message('DEBUG', 'logs/debug.log', f"trying send to kafka topic: {topic}")
            self.producer.produce(topic, json.dumps(data).encode('utf-8'))
            self.producer.flush()
            log_message('INFO', 'logs/kafka_info.log', "Terkirim ke kafka " + json.dumps(data))
        except Exception as e:
            log_message('ERROR', 'logs/error.log', f"error when trying send to kafka: {e}")
