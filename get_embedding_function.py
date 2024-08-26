from langchain.embeddings import HuggingFaceEmbeddings

def get_embedding_function():
    model_name = "sentence-transformers/all-mpnet-base-v2"  # You can change this to any other Hugging Face model
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    return embeddings
    
