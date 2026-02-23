import json
import boto3
import base64
import re
from datetime import datetime

REGION = "us-east-1"
bucket_name = "s3reconocimiento"

s3 = boto3.client("s3", region_name=REGION)
rekognition = boto3.client("rekognition", region_name=REGION)

def lambda_handler(event, context):
    try:
        body = base64.b64decode(event["body"])
        image_id = f"placa-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.jpg"

        s3.put_object(
            Bucket=bucket_name,
            Key=image_id,
            Body=body,
            ContentType="image/jpeg"
        )

        response = rekognition.detect_text(
            Image={'S3Object': {'Bucket': bucket_name, 'Name': image_id}}
        )

        placa_detectada = None

        for item in response["TextDetections"]:
            if item["Type"] == "LINE":
                texto = item["DetectedText"].upper()
                
                match = re.search(r'([A-Z]{3})[- ]?(\d{3})', texto)

                if match:
                    letras = match.group(1)
                    numeros = match.group(2)
                    placa_detectada = f"{letras}-{numeros}"
                    break

        image_url = f"https://{bucket_name}.s3.{REGION}.amazonaws.com/{image_id}"

        resultado = {
            "image_url": image_url,
            "placa": placa_detectada if placa_detectada else "No se detectó placa"
        }

        return {
            "statusCode": 200,
            "body": json.dumps(resultado)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }