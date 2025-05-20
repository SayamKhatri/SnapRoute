import os
import json
import base64
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import boto3
from pinecone import Pinecone


load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

with open("config.json") as f:
    config = json.load(f)

LOCAL_DATA_DIR = config["local_dataset_dir"]

bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

MAX_IMAGE_HEIGHT = 2048
MAX_IMAGE_WIDTH = 2048

def resize_and_get_bytes(image_path):
    image = Image.open(image_path)
    if (image.size[0] * image.size[1]) > (MAX_IMAGE_HEIGHT * MAX_IMAGE_WIDTH):
        image = image.resize((MAX_IMAGE_HEIGHT, MAX_IMAGE_WIDTH))
    with BytesIO() as output:
        image.save(output, format="PNG")
        return output.getvalue()

def get_image_embedding(image_path):
    try:
        bytes_data = resize_and_get_bytes(image_path)
        input_image = base64.b64encode(bytes_data).decode("utf-8")
        body = json.dumps({"inputImage": input_image})
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId="amazon.titan-embed-image-v1",
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response["body"].read())
        return response_body.get("embedding")
    except Exception as e:
        print(f"Failed embedding for {image_path}: {e}")
        return None

def get_all_image_files(data_dir):
    image_paths = []
    for category in os.listdir(data_dir):
        category_path = os.path.join(data_dir, category)
        if not os.path.isdir(category_path):
            continue
        for file in os.listdir(category_path):
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                image_paths.append((os.path.join(category_path, file), category))
    return image_paths

def upload_images_to_pinecone():
    vectors = []
    all_images = get_all_image_files(LOCAL_DATA_DIR)

    for image_path, label in all_images:
        embedding = get_image_embedding(image_path)
        if embedding:
            vector_id = f"{label}_{os.path.basename(image_path)}"
            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": {"label": label}
            })

    if vectors:
        index.upsert(vectors=vectors)
        print("Upload complete.")

if __name__ == "__main__":
    upload_images_to_pinecone()
