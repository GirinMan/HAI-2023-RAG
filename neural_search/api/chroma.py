import os
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from api.utils import sha256

client = chromadb.PersistentClient(path=os.environ["CHROMADB_PATH"])

emb_func = SentenceTransformerEmbeddingFunction(
    model_name= os.environ.get('EMBEDDING_MODEL'),
    device="cuda"
)

def create_collection(collection_name: str, metadata: dict = None):
    if not metadata:
        metadata = None
    return client.get_or_create_collection(name=collection_name,
                                        embedding_function=emb_func,
                                        metadata=metadata)
    
def check_collection(collection_name: str):
    return client.get_collection(collection_name)

def delete_collection(collection_name: str):
    return client.delete_collection(collection_name)

def index_documents(collection_name: str, document: dict):
    texts = [item.document for item in document]
    metadatas = [item.metadata for item in document]
    for i, metadata in enumerate(metadatas):
        if not metadata:
            metadatas[i] = None
    ids = [sha256(text) for text in texts]
    
    collection = client.get_collection(collection_name,
                                       embedding_function=emb_func)
    collection.upsert(
        documents=texts,
        metadatas=metadatas,
        ids=ids
    )

def search_documents(collection_name: str, query: str, top_k: int):
    collection = client.get_collection(collection_name,
                                       embedding_function=emb_func)
    results = collection.query(
        query_texts=query,
        n_results=top_k,
    )
    return results
