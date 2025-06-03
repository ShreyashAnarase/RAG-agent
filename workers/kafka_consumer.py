from kafka import KafkaConsumer, TopicPartition
import json
import os
import uuid

from sympy import true

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"



# Below version coz auto partition asisgnment was failing. 
from kafka import KafkaConsumer, TopicPartition
import json
import os
import time

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

USE_MANUAL_PARTITION = true
def get_kafka_consumer(topic: str, group_id: str = None, use_manual_partition: bool = USE_MANUAL_PARTITION) -> KafkaConsumer:
    consumer = KafkaConsumer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=None if use_manual_partition else group_id,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset='latest',  # <--- 'latest' ensures we don't re-read old messages
        enable_auto_commit=not use_manual_partition,
    )

    if use_manual_partition:
        print("🛠️ Manually assigning partition 0")
        tp = TopicPartition(topic, 0)
        consumer.assign([tp])
        print("✅ Manual assignment:", consumer.assignment())
    else:
        print(f"📡 Subscribing to topic: {topic}")
        consumer.subscribe([topic])
        timeout = time.time() + 5
        while not consumer.assignment():
            print("⏳ Waiting for partition assignment...")
            consumer.poll(timeout_ms=100)
            time.sleep(0.2)
            if time.time() > timeout:
                print("❌ Timeout waiting for assignment.")
                break
        print("✅ Assigned partitions:", consumer.assignment())

    return consumer

