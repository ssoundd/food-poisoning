from sitotoxism_data_loader import fetch_sitotoxism_data
from sitotoxism_doc_converter import create_document_from_data
from sitotoxism_chroma_updater import update_chroma
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

def update_sitotoxism():

    region_rows = fetch_sitotoxism_data("I2848")
    facility_rows = fetch_sitotoxism_data("I2849")
    virus_rows = fetch_sitotoxism_data("I2850")

    region_docs = create_document_from_data("region", region_rows)
    facility_docs = create_document_from_data("facility", facility_rows)
    virus_docs = create_document_from_data("virus", virus_rows)

    update_docs = region_docs + facility_docs + virus_docs

    update_chroma(update_docs)

def load_sitotoxism_chroma():

    vectorstore = Chroma(
        persist_directory = "./sitotoxism_db",
        embedding_function = OpenAIEmbeddings(model = "text-embedding-3-large"),
        collection_name = "s_db"
    )

    return vectorstore