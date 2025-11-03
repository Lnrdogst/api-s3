import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # Headers CORS para permitir requests desde cualquier origen
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
    }
    
    try:
        # Parsear el body JSON - manejar tanto string como dict
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
        
        # Validar campos requeridos
        bucket_name = body.get('bucket')
        prefix = body.get('prefix')
        
        if not bucket_name:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'bucket is required'})
            }
        
        if not prefix:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'prefix is required'})
            }
        
        # Validar que el prefijo termine con /
        if not prefix.endswith('/'):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'prefix must end with /'})
            }
        
        # Crear cliente S3
        s3_client = boto3.client('s3')
        
        # Crear el "directorio" poniendo un objeto vacío con el prefijo
        s3_client.put_object(
            Bucket=bucket_name,
            Key=prefix,
            Body=b'',  # Objeto vacío para simular directorio
            ContentType='application/x-directory'
        )
        
        return {
            'statusCode': 201,
            'headers': headers,
            'body': json.dumps({
                'bucket': bucket_name,
                'prefix': prefix
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