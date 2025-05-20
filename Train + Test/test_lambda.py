import uuid
from lambda_fn import lambda_handler

def generate_s3_event(bucket, key):
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": bucket},
                    "object": {"key": key}
                }
            }
        ]
    }

SOURCE_BUCKET = "complaints-landing-zone"
TEST_IMAGE_KEY = "front_test.png"  

# Simulate event
event = generate_s3_event(SOURCE_BUCKET, TEST_IMAGE_KEY)
response = lambda_handler(event, None)

print("\n--- Lambda Output ---")
print(response)
