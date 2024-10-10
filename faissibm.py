import os
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods, ModelTypes, EmbeddingTypes
from ibm_watsonx_ai import Credentials
from langchain_ibm import WatsonxEmbeddings, WatsonxLLM
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.docstore.document import Document
import docx2txt
import chardet

# File paths
vectordb_file_path = "faiss_watsonx_index"
csv_file_path = 'carbon_questionanswerpairs.csv'
report_file_path = 'carbon_footprint_report.docx'

# Global variables
vectordb = None
watsonx_llm = None
report_content = None

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    return chardet.detect(raw_data)['encoding']

def create_vector_db():
    global vectordb
    try:
        encoding = detect_encoding(csv_file_path)
        df = pd.read_csv(csv_file_path, encoding=encoding)
        
        documents = []
        for _, row in df.iterrows():
            question = row['question']
            answer = row['answer']
            doc = Document(page_content=f"Question: {question}\nAnswer: {answer}", metadata={'question': question, 'answer': answer})
            documents.append(doc)

        embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        vectordb = FAISS.from_documents(documents=documents, embedding=embeddings)
        vectordb.save_local(vectordb_file_path)
        return True, "Vector database created successfully!"
    except Exception as e:
        return False, f"Error creating vector database: {str(e)}"

def load_faiss_vector_db():
    global vectordb
    try:
        embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        vectordb = FAISS.load_local(vectordb_file_path, embeddings, allow_dangerous_deserialization=True)
        return True, "Vector database loaded successfully."
    except Exception as e:
        return False, f"Error loading vector database: {str(e)}"

def setup_watsonx():
    global watsonx_llm
    try:
        credentials = Credentials(
            url="https://us-south.ml.cloud.ibm.com",
            api_key="Enter your api key here"
        )

        project_id = os.environ.get("PROJECT_ID", "Enter your project ID here")

        model_id = ModelTypes.GRANITE_13B_CHAT_V2
        parameters = {
            GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
            GenParams.MIN_NEW_TOKENS: 1,
            GenParams.MAX_NEW_TOKENS: 500,
            GenParams.STOP_SEQUENCES: ["Question:","Report:","Explanation:","\n\n"]
        }
        watsonx_llm = WatsonxLLM(
            model_id=model_id.value,
            url=credentials.get("url"),
            apikey=credentials.get("apikey"),
            project_id=project_id,
            params=parameters
        )
        return True, "WatsonX set up successfully."
    except Exception as e:
        return False, f"Error setting up WatsonX: {str(e)}"

def read_docx():
    global report_content
    try:
        report_content = docx2txt.process(report_file_path)
        return True, "Report loaded successfully."
    except Exception as e:
        return False, f"Error reading DOCX file: {str(e)}"

def initialize_system():
    global vectordb, watsonx_llm, report_content
    
    # Step 1: Create or load vector database
    if not os.path.exists(vectordb_file_path):
        success, message = create_vector_db()
        if not success:
            return False, message
    
    success, message = load_faiss_vector_db()
    if not success:
        return False, message
    
    # Step 2: Setup WatsonX
    success, message = setup_watsonx()
    if not success:
        return False, message
    
    # Step 3: Read the report
    success, message = read_docx()
    if not success:
        return False, message
    
    return True, "System initialized successfully."

def process_question(question):
    global vectordb, watsonx_llm, report_content
    
    if not all([vectordb, watsonx_llm, report_content]):
        return "Error: System not fully initialized. Please restart the application."

    try:
        similar_docs = vectordb.similarity_search(question, k=1)
        if similar_docs:
            context = similar_docs[0].page_content
        else:
            context = "No closely related information found in the database."

        rag_prompt_template = PromptTemplate(
            input_variables=["context", "question", "report"],
            template="""You are an AI assistant named CarbonBuddy specializing in carbon emissions and environmental topics. 
Use the following context, report, and your general knowledge to answer the question.
Always consider the report content when formulating your answer, even for general questions.
If the context is relevant, incorporate it into your answer.
If neither the context nor the report contain relevant information, answer based on your own knowledge.
Provide a concise and focused answer in a single paragraph without adding extra questions or unrelated information.

Context: {context}
Report: {report}
Question: {question}

Answer:"""
        )
        llm_chain = LLMChain(llm=watsonx_llm, prompt=rag_prompt_template)
        
        response = llm_chain.run(context=context, question=question, report=report_content)
        
        # Post-process the response to ensure it's a single paragraph
        #response = response.strip()  # Remove leading/trailing whitespace
        response = response.split('\n\n')[0]  # Take only the first paragraph if multiple exist
        #response = response.replace('\n', ' ')  # Replace any newlines within the paragraph with spaces
        
        return response
    except Exception as e:
        return f"Error processing question: {str(e)}"

if __name__ == "__main__":
    print("This script is designed to be imported and used by the web interface.")
    
