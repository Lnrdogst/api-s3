import boto3
import json

def lambda_handler(event, context):
    # Headers CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
    }
    
    try:
        # Entrada (json) - manejar tanto string como dict
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
        
        nombre_bucket = body.get('bucket')
        if not nombre_bucket:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'bucket is required'})
            }
        
        # Proceso    
        s3 = boto3.client('s3')
        response = s3.list_objects(Bucket=nombre_bucket)
        lista = []
        if 'Contents' in response:
            for obj in response['Contents']:
                lista.append(obj['Key'])

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'bucket': nombre_bucket,
                'lista_objetos': lista
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
