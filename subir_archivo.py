import json
import boto3
import base64
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # Headers CORS para todas las respuestas
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
    }
    
    try:
        # Parsear el JSON del body
        if 'body' in event and event['body']:
            body = json.loads(event['body'])
        else:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Missing request body'})
            }
        
        # Validar campos requeridos
        bucket_name = body.get('bucket')
        key = body.get('key')
        content_base64 = body.get('contentBase64')
        content_type = body.get('contentType', 'application/octet-stream')
        
        if not bucket_name:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'bucket is required'})
            }
        
        if not key:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'key is required'})
            }
        
        if not content_base64:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'contentBase64 is required'})
            }
        
        # Decodificar el contenido base64
        try:
            file_content = base64.b64decode(content_base64)
        except Exception as e:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': f'Invalid base64 content: {str(e)}'})
            }
        
        # Crear cliente S3
        s3_client = boto3.client('s3')
        
        # Subir el archivo al bucket
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=file_content,
            ContentType=content_type
        )
        
        return {
            'statusCode': 201,
            'headers': headers,
            'body': json.dumps({
                'bucket': bucket_name,
                'key': key
            })
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        if error_code == 'NoSuchBucket':
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Bucket does not exist'})
            }
        elif error_code == 'AccessDenied':
            return {
                'statusCode': 403,
                'headers': headers,
                'body': json.dumps({'error': 'Access denied to bucket'})
            }
        else:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': f'AWS error: {error_code}'})
            }
    
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }