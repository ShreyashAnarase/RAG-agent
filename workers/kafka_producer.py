from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_to_kafka(topic: str, value: dict):
    producer.send(topic, value=value)
    producer.flush()
    print(f" Saving data to the topic {topic}")
