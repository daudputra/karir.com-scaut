from confluent_kafka import Producer as ConfluentProducer
from src.helper.mylog import log_message
import asyncio
import json

class Producer:
    def __init__(self, bootstrap_servers: list) -> None:
        conf = {'bootstrap.servers': ','.join(bootstrap_servers)}
        self.producer = ConfluentProducer(conf)
    
    async def send(self, topic, data: dict):
        try:
            await log_message('DEBUG', 'logs/debug.log', f"trying to send to kafka topic: {topic}")
            
            await asyncio.to_thread(self.producer.produce, topic, json.dumps(data).encode('utf-8'))
            await asyncio.to_thread(self.producer.flush)
            
            await log_message('INFO', 'logs/kafka_info.log', f"Terkirim ke kafka")
            # await log_message('INFO', 'logs/kafka_info.log', f"Terkirim ke kafka: {json.dumps(data)}")
        except Exception as e:
            await log_message('ERROR', 'logs/error.log', f"Error when trying to send to kafka: {e}")