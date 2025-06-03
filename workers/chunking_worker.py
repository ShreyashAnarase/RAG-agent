# Consumes uploaded documents from the Kafka topic 
# SPlits into Chunks 
# Forwards Chunks to Another Kafka topic for embedding 
from pdb import run
import torch 
from kafka_consumer import get_kafka_consumer
from kafka_producer import send_to_kafka
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
import signal, sys
from config import DOCUMENTS_TOPIC,CHUNKS_TOPIC
from uuid import uuid4
from kafka import TopicPartition


# consumer = get_kafka_consumer(DOCUMENTS_TOPIC,use_manual_partition=True,partition=0)
consumer = get_kafka_consumer(DOCUMENTS_TOPIC, group_id="chunking-worker-group")
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=100)

# Consume from documents-uploaed topic -> split to Chunks -> send to Chunks topic
# each document upload -> one Kafka message
# Loop to  keep consuming new documents as they arrive, a listenr


running = True

def shutdown_handler(sig, frame):
    global running
    print(" \n Shutting down Chunking worker ")
    running = False
    consumer.close()
    sys.exit(0)

# Attach signal handler
signal.signal(signal.SIGINT, shutdown_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, shutdown_handler)  # Docker stop, etc.

print("✅ Chunking worker started. Waiting for Uploaded documents ...")
print("Subscribing to topic:", DOCUMENTS_TOPIC)

try:
    while running:

        for msg in consumer:
            print(" Entering the msg loop")
            doc = msg.value
            doc_id = doc.get("doc_id")
            content = doc.get("content")
            

            if not doc_id or not content:
                print(" Invalid message in topic, skipping")
                continue
            
            print(f"✅ Chunking the document {doc_id} ")
            chunks = splitter.split_text(content)
            for i,chunk_text in enumerate(chunks):
                chunk_payload = { "doc_id" : doc_id, "chunk_id" : i, "text": chunk_text }
                send_to_kafka(CHUNKS_TOPIC, chunk_payload)
            
            print(f" Document '{doc_id}' chunked and sent to an embedding queue. SPlit into {len(chunks)} chunks ")

            if not running:
                break

#Shutdown worker wit Ctrl +C 
except KeyboardInterrupt:
    shutdown_handler(None,None)
