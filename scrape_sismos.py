import requests
from bs4 import BeautifulSoup
import boto3
import uuid

def lambda_handler(event, context):
    url = "https://ultimosismo.igp.gob.pe/ultimo-sismo/sismos-reportados"

    # Solicitud HTTP
    response = requests.get(url)
    if response.status_code != 200:
        return {'statusCode': response.status_code, 'body': 'Error al acceder a la página web'}

    soup = BeautifulSoup(response.content, 'html.parser')

    # Encontrar la tabla principal
    table = soup.find('table', class_='table table-hover table-bordered table-light border-white w-100')
    if not table:
        return {'statusCode': 404, 'body': 'No se encontró la tabla de sismos'}

    # Extraer todas las filas de sismos (omitimos el encabezado)
    rows_html = table.find('tbody').find_all('tr')

    # Tomar solo los últimos 10 sismos
    rows_html = rows_html[:10]

    sismos = []
    for tr in rows_html:
        cells = tr.find_all('td')
        if len(cells) < 5:
            continue  # evitar filas incompletas

        fuente_ref = cells[0].get_text(separator=' ', strip=True)  # "IGP/CENSIS/RS 2025-0763"
        ubicacion = cells[1].text.strip()
        fecha_hora = cells[2].text.strip()
        magnitud = cells[3].text.strip()
        enlace = cells[4].find('a')['href'] if cells[4].find('a') else ''

        sismos.append({
            'id': str(uuid.uuid4()),
            'FuenteReferencia': fuente_ref,
            'Ubicacion': ubicacion,
            'FechaHora': fecha_hora,
            'Magnitud': magnitud,
            'EnlaceReporte': enlace
        })

    # Guardar en DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table_db = dynamodb.Table('WebScrappingSismos')

    # Limpiar tabla antes de insertar
    scan = table_db.scan()
    with table_db.batch_writer() as batch:
        for item in scan.get('Items', []):
            batch.delete_item(Key={'id': item['id']})

    # Insertar nuevos registros
    with table_db.batch_writer() as batch:
        for sismo in sismos:
            batch.put_item(Item=sismo)

    return {'statusCode': 200, 'body': sismos}