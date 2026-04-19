from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List
from langchain_core.documents import Document


# Extract Text from PDF files
def load_pdf_files(data):
    loader = DirectoryLoader(
        data,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )

    documents = loader.load()
    return documents


# Convert the long content into minimal
def filter_to_minimal_docs(docs: List[Document]) -> List[Document]:
    """Given a list of Document objects, return a new list of Document objects containing only 'Source' in metadata and the original page_content.
    """

    minimal_docs: List[Document] = []

    for doc in docs:
        src = doc.metadata.get("source")
        minimal_docs.append(
            Document(
                page_content=doc.page_content,
                metadata={"source": src}
            )
        )
    return minimal_docs


# Split the documents into the smaller chunks
def text_split(extracted_data):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=50,
        length_function=len,
        # Respects paragraph/sentence boundaries
        separators=["\n\n", "\n", ".", " "]
    )
    texts_chunk = text_splitter.split_documents(extracted_data)
    return texts_chunk


# Download the Embeddings from Huggingface
def download_embeddings():
    """Download and return the HuggingFace embeddings model.
    """

    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": False}

    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )
    return embeddings
