from langchain_community.chat_models import ChatOCIGenAI
from langchain_core.messages import HumanMessage,SystemMessage, AIMessage
from langchain_community.embeddings import OCIGenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import XMLOutputParser, StrOutputParser
from tenacity import retry
from ociGenAI.app.embedding import Embedding
from langchain_community.vectorstores import Chroma
from langchain.schema.runnable import RunnablePassthrough
import config   
import os

msg = "tell me a joke."

def get_response(msg):
  chat = create_chat_object()
  messages = [
    HumanMessage(content=msg)
  ]
  response = chat.invoke(messages)
  return response.content


def get_context_based_resp(msg, context):
  prompt_template = ChatPromptTemplate.from_template(config.PROMPT_TEMPLATE_1)
  query_model = create_chat_object()

  chain = (
      RunnablePassthrough.assign(context=lambda _: context)
      | prompt_template
      | query_model
      | StrOutputParser()
  )
  response = chain.invoke({ "question": msg})
  print(response)
  return response


def create_chat_object():
  chat = ChatOCIGenAI(
    model_id=config.model_id,
    service_endpoint=config.endpoint,
    compartment_id=config.COMPARTMENT_ID,
    provider=config.PROVIDER,
    model_kwargs= config.args,
    auth_type=config.AUTH_TYPE,
    auth_profile=config.CONFIG_PROFILE,
    auth_file_location = config.auth_file_location
  )

  return chat

#Get  embeddings similar to the query embedding vector  from DB 
# to pass as context to LLM
def get_context_from_DB(query):
    em = Embedding()
    embedding_vector = em.embed(query) 
    try:
        db = Chroma(persist_directory=config.CHROMA_PATH, embedding_function=HuggingFaceEmbeddings)
 
        docs = db.similarity_search_by_vector(embedding = [embedding_vector], k = 5)
        print("Number of documents returned " + str(len(docs)))
        context_str = "\n".join(doc.page_content for doc in docs)
        return context_str

    except Exception as e:
            if not os.path.exists(config.CHROMA_PATH):
                print("Chroma DB not found at path:", config.CHROMA_PATH)
                return "No context found. DB might be empty."
            
            else:
                print(" Falied to get context from DB:   ", str(e))
                return "Error retrieving context from DB."

    


if __name__ == "__main__":
  context = get_context_from_DB(" Which is the main character")
  # print(context)
  RAG_response = get_context_based_resp(" Which is the main character",context= context )
  # print(RAG_response)

  
  
