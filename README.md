# OnPremLLM

OnPremLLM is a project designed to simplify document embedding and querying. It provides an automated workflow to create embeddings for documents and enables querying with image responses using a GROQ API. The project includes a Flask-based API, a Streamlit frontend, and supports integration with Qdrant for storage.

## Architecture of System
![Alt text](https://github.com/vaibhavsd-av/OnPremLLM/blob/main/OnpremLLM.png)

## Features

- **Automated Document Embeddings**: Automatically generates embeddings for all documents in the docs folder.
- **Image Storage**: Stores generated embeddings as images with unique names in the images folder.
- **Query Support**: Query documents and receive responses enhanced with images using GROQ API. 
- **User-Friendly Interfaces**: Includes a RESTful API powered by Flask and a web frontend built with Streamlit.
- **Notebook Support**: Includes QDRANT_COLQWEN.ipynb for experimentation in a Jupyter Notebook.

## Getting Started

### Prerequisites

1. Clone the repository:
   ```bash
   git clone https://github.com/vaibhavsd-av/OnPremLLM.git
   cd OnPremLLM
   ```

2. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  
   # On Windows, use `venv\Scripts\activate`
   ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a .env file in the project root and add your GROQ API key:
   ```env
   GROQ_KEY="your_groq_api_key_here"
   ```

### Folder Structure

- **docs**: Create this folder in the project root and place your documents (PDFs) here. Embeddings will be generated automatically for these documents..
- **images**: Create this folder in the project root. Generated embeddings will be saved in this folder as images with unique names.
- **handlers/watcher.py**: Monitors the docs folder and creates embeddings for any new documents.
- **api/app.py**: Flask application for the backend API.
- **frontend/main.py**: Streamlit application for the frontend interface.
- **QDRANT_COLQWEN.ipynb**: Jupyter Notebook with relevant code for working with embeddings and querying.

## Usage

### Running the Backend API

1. Start the Flask API server:
   ```bash
   flask --app api/app.py run
   ```

### Running the Frontend

1. Launch the Streamlit application:
   ```bash
   streamlit run frontend/main.py
   ```

### Generating Embeddings

1. Place your documents in the docs folder.
2. The watcher.py script will automatically generate embeddings for the documents.
3. Generated embeddings will be saved in the images folder with unique names.

### Querying with GROQ API (Online Mode)

1. Ensure your .env file contains a valid GROQ API key.
2. Use the frontend or backend API to send queries and receive answers along with images.

### Querying with Local System

1. Use ```get_response_offline``` instead of ```get_response``` in api/app.py.
   ```
   from helpers.generate_answer import get_response_offline

   # response = get_response(image_path, query_text, history)
   response = get_response_offline(image_path, query_text)
    ```
2. To get more tokens in the output from the model, you can adjust the ```max_new_tokens``` parameter when calling the generate method. The ```max_new_tokens``` parameter controls the maximum number of tokens the model can generate in response to your input.
example:
```
output_ids = model.generate(**inputs, max_new_tokens=1000)
```


### NOTE: 
When using offline mode, it will require high computational power and it will be time consuming process.


## Setting Up Qdrant for Storing Embeddings

Qdrant is a vector search engine that can store and retrieve document embeddings efficiently. Follow these steps to set up Qdrant using Docker:

### Prerequisites

1. Ensure Docker is installed on your system. You can download it from [Docker's official site](https://www.docker.com/).

### Steps to Set Up Qdrant

1. **Pull the Qdrant Docker Image**:
   
   Run the following command to pull the latest Qdrant Docker image:
   ```bash
   docker pull qdrant/qdrant
   ```

2. **Run the Qdrant Docker Container**:
   
   Start a Qdrant container using the following command:
   ```bash
   docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
  
3. **Verify Qdrant is Running**:
   
   Open a web browser and navigate to `http://localhost:6333/health`. If Qdrant is running, you will see a health check response like:
   ```json
   {"status":"ok"}
   ```

### Integrating Qdrant with OnPremLLM

1. **Store Embeddings in Qdrant**:

   When embeddings are generated, they will be automatically sent to the Qdrant instance for storage, enabling efficient retrieval during queries.

2. **Query Embeddings**:

   Use the backend API to query embeddings stored in Qdrant.

## Notebook Usage

For experimentation and detailed workflows, use the QDRANT_COLQWEN.ipynb Jupyter Notebook. It contains all necessary code to:

- Generate embeddings
- Query the stored data
- Integrate with Qdrant

## Requirements

All required Python packages are listed in requirements.txt. Install them using:
```bash
pip install -r requirements.txt
```

## Environment Variables

Create a .env file in the project root with the following content:
```env
GROQ_KEY="your_groq_api_key_here"
```

## Docker Setup

To run the project using Docker, follow the steps below:

**Build the Docker Image**:
   From the root of the project, run:
   ```bash
   docker up --build
   ```