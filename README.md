# Carbon Footprint Q&A System

This project implements a question-answering system focused on carbon emissions and environmental topics. It uses IBM WatsonX AI, FAISS for vector storage, and LangChain for prompt engineering and chain management.

## Features

- Create and manage a vector database of carbon-related Q&A pairs
- Utilize IBM WatsonX AI for natural language processing
- Process and answer questions based on a carbon footprint report and pre-existing Q&A pairs
- Implement Retrieval-Augmented Generation (RAG) for more accurate and context-aware responses

## Prerequisites

- Python 3.7+
- IBM Cloud account with WatsonX AI service
- The required Python packages (see `requirements.txt`)

## Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-name>
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your IBM Cloud credentials:
     ```
     IBM_CLOUD_API_KEY=your_api_key_here
     PROJECT_ID=your_project_id_here
     ```

4. Prepare your data:
   - Place your carbon Q&A pairs CSV file in the project directory as `carbon_questionanswerpairs.csv`
   - Place your carbon footprint report DOCX file in the project directory as `carbon_footprint_report.docx`

## Usage

This script is designed to be imported and used by a web interface. The main components are:

- `initialize_system()`: Sets up the vector database, WatsonX, and loads the report
- `process_question(question)`: Processes a user's question and returns an answer

To use in your application:

```python
from your_script_name import initialize_system, process_question

success, message = initialize_system()
if success:
    while True:
        question = input("Ask a question (or 'quit' to exit): ")
        if question.lower() == 'quit':
            break
        answer = process_question(question)
        print(f"Answer: {answer}")
else:
    print(f"Initialization failed: {message}")
```

##Streamlit interface implemetation
```
   streamlit run carbonbuddy.py
   ```

## File Descriptions

- `main.py`: The main script containing all the logic for the Q&A system
- `carbon_questionanswerpairs.csv`: CSV file containing pre-existing Q&A pairs
- `carbon_footprint_report.docx`: DOCX file containing the carbon footprint report
- `requirements.txt`: List of Python package dependencies
- `README.md`: This file, containing project information and setup instructions

## Note

Ensure that you have the necessary permissions and comply with IBM Cloud's terms of service when using the WatsonX AI service.

## License

MIT License.See documentation of the license for more info.

## Contributing

kdurgaprasadkavali@gmail.com
