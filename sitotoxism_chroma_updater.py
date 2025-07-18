from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

def update_chroma(new_docs : list):

    vectorstore = Chroma(
        persist_directory = "./sitotoxism_db",
        collection_name = "s_db",
        embedding_function = OpenAIEmbeddings(model = "text-embedding-3-large")
    )

    existing = vectorstore.get(include = ["metadatas"])
    existing_keys = {(m["source"], m["sitotoxism_id"]) for m in existing["metadatas"]}

    to_upsert = [doc for doc in new_docs if (doc.metadata["source"], doc.metadata["sitotoxism_id"]) not in existing_keys]

    if to_upsert:
        vectorstore.add_documents(to_upsert)
        vectorstore.persist()
        print(f"{len(to_upsert)}건의 문서가 새로 저장되었습니다.")

    else:
        print("업데이트할 문서가 없습니다.")