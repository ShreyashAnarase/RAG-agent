# Create embeddings using HuggingFaceEmbeddings

from langchain_huggingface import HuggingFaceEmbeddings
from langchain.evaluation import load_evaluator,EvaluatorType, embedding_distance

class Embedding:
    def __init__(self):
        self.model_name = "sentence-transformers/all-mpnet-base-v2"
        self.model_kwargs = {'device': 'cpu'}
        self.encode_kwargs = {'normalize_embeddings': False}
        self.hf = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs=self.model_kwargs,
            encode_kwargs=self.encode_kwargs
        )    
    

    def embed(self,text):  
        vector = self.hf.embed_query(text)
        return vector
        # document = self.hf.embed_documents([text])


    # # compare the embed vector of two words -    HOW SIMILAR 
    # def compare_embedding_pairwise_distance(self,a,b):
    #     # # The types of the evaluators.   PAIRWISE_STRING_DISTANCE,EMBEDDING_DISTANCE , STRING_DISTANCE... 

    #     hf_evaluator = load_evaluator(EvaluatorType.PAIRWISE_EMBEDDING_DISTANCE, embeddings=self.hf)
    #     x = hf_evaluator.evaluate_string_pairs(prediction=a, prediction_b=b)
    #     print(f"Comparing USING {EvaluatorType.PAIRWISE_EMBEDDING_DISTANCE} ({a}, {b}): {x}")

    # def compare_embedding_distance(self,a,b):
    #     hf_evaluator = load_evaluator(EvaluatorType.EMBEDDING_DISTANCE,embeddings = self.hf)
    #     x = hf_evaluator.evaluate_strings(prediction=a, reference=b)
    #     print(f"Comparing using {EvaluatorType.EMBEDDING_DISTANCE} ({a}, {b}): {x}")
        


# if __name__ == "__main__" :
#     emb = Embedding()
#     emb.embed('applebees')
#     emb.compare_embedding_distance("Cat", "Dog")

