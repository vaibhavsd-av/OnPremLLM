from flask import Flask, request, jsonify
import os
import time

from helpers.query import process_query_to_vector
from helpers.groq_helper import get_response
from helpers.qdrant_search import search_img_id
from helpers.generate_answer import get_response_offline

app = Flask(__name__)

history = []

# Query endpoint
@app.route('/api/query')
def query():
    start_time = time.time()  # Start timing the function call

    query_text = request.json.get("query")
    if not query_text:
        return jsonify({"error": "No query text provided"}), 400

    # Measure time for processing query
    query_start_time = time.time()
    multivector_query = process_query_to_vector(query_text)
    query_end_time = time.time()
    print(f"process_query_to_vector execution time: {query_end_time - query_start_time:.4f} seconds")

    # Measure time for image search
    search_start_time = time.time()
    img_id = search_img_id(multivector_query)
    search_end_time = time.time()
    print(f"search_img_id execution time: {search_end_time - search_start_time:.4f} seconds")

    # Construct image path
    image_path = os.path.join('images', f'{img_id}.jpg')

    # Measure time for getting the response
    response_start_time = time.time()
    # response = get_response(image_path, query_text, history)
    response = get_response_offline(image_path, query_text)
    response_end_time = time.time()
    print(f"get_response execution time: {response_end_time - response_start_time:.4f} seconds")

    # Add the current chat to history (only keep last 2 chats)
    if len(history) >= 3:
        history.pop(0)  # Remove the oldest history entry if there are more than 2
    history.append({
        "query": query_text,
        "answer": response,
        "image_path": image_path,
    })

    end_time = time.time()  # End timing the function call
    print(f"Total execution time for query: {end_time - start_time:.4f} seconds")

    return jsonify({
        "answer": f'{response}',
        "query": query_text,
    })


if __name__ == '__main__':
    app.run(debug=True)
