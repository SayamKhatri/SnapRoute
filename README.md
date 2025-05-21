# SnapRoute - Serverless Image Classification with AWS and Pinecone

**SnapRoute** is a fully serverless image classification pipeline designed to automatically label and organize incoming image data using similarity-based classification. 

When a new image is uploaded to an S3 bucket, SnapRoute triggers a Lambda function that processes the image, finds the most similar image from a training dataset using Pinecone, assigns the appropriate label, and moves the image to a structured destination bucket.
This kind of labeling is often done manually by humans, SnapRoute automates it with near real-time performance.

# Tech Stack

- **AWS Lambda** – Serverless execution
- **Amazon Bedrock (Titan model)** – Embedding generation for images
- **Pinecone** – Vector similarity search
- **Amazon S3** – Input/output image storage
- **Docker** – Containerized Lambda function
- **ECR** – Container registry


# Use Cases

### Insurance
- Automatically label damage photos (front, rear, side) for vehicle claims
- Pre-process claim images for faster downstream handling

### Healthcare
- Organize and label medical imaging (e.g., CT scans, MRIs) by body region or abnormality
- Pre-tag patient scans before radiologist review

### Manufacturing
- Classify defective vs. non-defective parts from production line photos
- Label machine components in maintenance logs

### Logistics & Warehousing
- Auto-categorize images of damaged shipments
- Organize proof-of-delivery photos by type or location

### Retail & E-commerce
- Tag product images by category (e.g., "shoes", "jackets", "accessories")
- Group user-uploaded product photos by visual similarity

