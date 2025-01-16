from PIL import Image
import torch
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor, pipeline
import gc

# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the regular precision model (non-AWQ version)
model = Qwen2VLForConditionalGeneration.from_pretrained("Qwen/Qwen2-VL-2B-Instruct")
model = model.to(device)

processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-2B-Instruct")


# Function to run the model on an example
def get_response_offline(image_path, query_text):
    # Image
    try:
        image = Image.open(image_path)
        # Resize the image to reduce memory usage (optional)
        image = image.resize((256, 256),  Image.LANCZOS)  # Adjust this size as needed
    except Exception as e:
        print(f"Error loading image: {e}")
        exit()

    conversation = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"text": query_text},
            ],
        }
    ]

    # Preprocess the inputs
    text_prompt = processor.apply_chat_template(conversation, add_generation_prompt=True)
    inputs = processor(
        text=[text_prompt], images=[image], padding=True, return_tensors="pt"
    )

    # Move the inputs to the device (CPU)
    inputs = inputs.to(device)

    # Ensure no gradients are tracked during inference
    with torch.no_grad():
        try:
            output_ids = model.generate(**inputs, max_new_tokens=500)
            generated_ids = [
                output_ids[len(input_ids):]
                for input_ids, output_ids in zip(inputs.input_ids, output_ids)
            ]
            output_text = processor.batch_decode(
                generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True
            )
        except Exception as e:
            print(f"Error during model inference: {e}")

    # Clear memory after inference
    gc.collect()  # Explicitly free up memory
    torch.cuda.empty_cache()  # Clear GPU memory if you were using CUDA

    return output_text[0]