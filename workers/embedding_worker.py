from torch import embedding
from kafka_consumer import get_kafka_consumer
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
import signal
import sys
import os
import uuid
from config import CHROMA_PATH, CHUNKS_TOPIC


embedding_model = HuggingFaceEmbeddings()
vectorstore = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=embedding_model
)

# consumer = get_kafka_consumer(CHUNKS_TOPIC,use_manual_partition=True,partition=0)
consumer = get_kafka_consumer(CHUNKS_TOPIC,group_id="embedding-worker-group")

running = True
chunk_counter = 0
persist_interval = 10  # Persist every 10 chunks


def shutdown_handler(sig, frame):
    global running
    print("\n Shutting down embedding worker...")
    running = False
    consumer.close()
    vectorstore.persist()  # Persist changes to disk
    print("Embeddings saved to Chroma and Kafka consumer closed.")
    sys.exit(0)
# Attach graceful shutdown
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

print("✅ Embedding worker started. Waiting for chunks...")

try:
    while running:
        for message in consumer:
            chunk = message.value
            doc_id = chunk.get("doc_id")
            chunk_id = chunk.get("chunk_id")
            text = chunk.get("text")

            if not doc_id or not text:
                print(" Skipping invalid chunk:", chunk)
                continue

            # Wrap into LangChain document
            doc = Document(
                page_content=text,
                metadata={
                    "doc_id": doc_id,
                    "chunk_id": chunk_id,
                    "uuid": str(uuid.uuid4())
                }
            )

            # Add to vector store
            vectorstore.add_documents([doc])
            print(f"Embedded chunk #{chunk_id} of doc {doc_id}")

            chunk_counter += 1
            if chunk_counter % persist_interval == 0:
                vectorstore.persist()
                print(f" Auto-persisted after {chunk_counter} chunks.")

            if not running:
                break

except KeyboardInterrupt:
    shutdown_handler(None, None)
