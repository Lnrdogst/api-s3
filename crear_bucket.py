import json
import boto3
import re
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # Configurar CORS para permitir requests desde cualquier origen
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
    }
    
    try:
        # Parsear el body JSON de la request - manejar tanto string como dict
        if 'body' in event and event['body']:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']  # Ya es un dict
        else:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Missing request body'})
            }
        
        # Validar que venga el nombre del bucket
        bucket_name = body.get('bucketName')
        if not bucket_name:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'bucketName is required'})
            }
        
        # Validar formato del nombre (minúsculas, sin espacios, sin guiones bajos)
        if not re.match(r'^[a-z0-9.-]+$', bucket_name) or '__' in bucket_name or ' ' in bucket_name:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Invalid bucket name format'})
            }
        
        # Crear cliente S3
        s3_client = boto3.client('s3')
        
        # Obtener la región del provider (por defecto us-east-1)
        region = boto3.Session().region_name or 'us-east-1'
        
        # Crear el bucket
        if region == 'us-east-1':
            # Para us-east-1 no se necesita CreateBucketConfiguration
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            # Para otras regiones sí se necesita especificar la configuración
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        
        return {
            'statusCode': 201,
            'headers': headers,
            'body': json.dumps({'bucket': bucket_name})
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        if error_code in ['BucketAlreadyExists', 'BucketAlreadyOwnedByYou']:
            return {
                'statusCode': 409,
                'headers': headers,
                'body': json.dumps({'error': 'Bucket already exists or is owned by someone else'})
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