#!/bin/bash

# Wait for Qdrant to be ready
echo "Waiting for Qdrant to be available..."
while ! curl -s http://qdrant:6333; do
  echo "Qdrant is not available, retrying..."
  sleep 5
done
echo "Qdrant is available!"

# Start the watcher process in the background
echo "Starting the watcher process..."
python3 handlers/watcher.py &

# Start the Flask API in the background, binding to 0.0.0.0
echo "Starting Flask API..."
flask --app api/app.py run --host=0.0.0.0 --port=5000 &

# Start the Streamlit app, binding to 0.0.0.0
echo "Starting Streamlit..."
streamlit run frontend/main.py --server.headless true
