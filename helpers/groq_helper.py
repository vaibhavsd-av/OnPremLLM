import os
from groq import Groq
import base64

client = Groq(
    api_key=os.environ.get('GROQ_KEY'),
)

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
  

def get_response(image_path, query_text, history):
    # Getting the base64 string of the image
    base64_image = encode_image(image_path)
    
    # Prepare the messages for the chat including the conversation history
    messages = []
    
    # Add past conversation history as messages for context
    for entry in history:
        messages.append({"role": "user", "content": entry["query"]})
        messages.append({"role": "assistant", "content": entry["answer"]})
    
    # Add the current user query and image to the messages
    messages.append({
        "role": "user",
        "content": [
            {"type": "text", "text": query_text},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}",
                },
            },
        ]
    })
    
    # Call the Groq model to get a response
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.2-11b-vision-preview",
        # max_tokens=300
    )
    
    response = chat_completion.choices[0].message.content

    # Return the response
    return response
