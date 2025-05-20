import json
import boto3
import base64
import os
import io
from PIL import Image
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

MAX_IMAGE_HEIGHT = 2048
MAX_IMAGE_WIDTH = 2048
CONFIDENCE_THRESHOLD = 0.5  

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
DESTINATION_BUCKET = os.getenv("DESTINATION_BUCKET", "snaproute-output")

bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
s3 = boto3.client("s3")
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

def image_embedding(bytes_data):
    input_image = base64.b64encode(bytes_data).decode("utf8")
    body = json.dumps({"inputImage": input_image})
    response = bedrock_runtime.invoke_model(
        body=body,
        modelId="amazon.titan-embed-image-v1",
        accept="application/json",
        contentType="application/json"
    )
    response_body = json.loads(response.get("body").read())
    return response_body.get("embedding")

def lambda_handler(event, context):
    print(f"📥 Received event: {json.dumps(event)}")

    try:
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = event["Records"][0]["s3"]["object"]["key"]
        print(f"🔍 Processing: {bucket}/{key}")

        # Get image from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        image_data = response["Body"].read()

        # Resize image
        image = Image.open(io.BytesIO(image_data))
        image = image.resize((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT))

        # Convert to bytes
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        image_bytes = buffer.read()

        # Get embedding
        embedding = image_embedding(image_bytes)

        # Query Pinecone
        query_response = index.query(
            vector=embedding,
            include_metadata=True,
            top_k=1
        )

        match = query_response["matches"][0]
        score = match["score"]
        predicted_label = match["metadata"]["label"]

        if score < CONFIDENCE_THRESHOLD:
            predicted_label = "uncertain"
            print(f"Low confidence ({score:.2f}), classifying as 'uncertain'")
        else:
            print(f"Classified as '{predicted_label}' with score {score:.2f}")

        # Construct new key
        new_key = f"{predicted_label}/{os.path.basename(key).lower()}"

        # Copy image to new S3 location
        s3.copy_object(
            Bucket=DESTINATION_BUCKET,
            CopySource={"Bucket": bucket, "Key": key},
            Key=new_key,
            ContentType="image/png"
        )

        # Optionally delete original
        s3.delete_object(Bucket=bucket, Key=key)
        print(f"Moved image to {DESTINATION_BUCKET}/{new_key}")

        return {
            "statusCode": 200,
            "body": json.dumps(f"Classified as {predicted_label} and moved to {new_key}")
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error: {str(e)}")
        }
