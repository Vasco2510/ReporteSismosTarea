import json
import boto3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import uuid
from datetime import datetime

def lambda_handler(event, context):
    print("🚀 Iniciando scraping de sismos...")
    
    try:
        # Configurar Chrome para Lambda (AWS Academy)
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1280x1696')
        chrome_options.add_argument('--single-process')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-dev-tools')
        chrome_options.add_argument('--no-zygote')
        
        # Usar Chrome preinstalado en Lambda
        driver = webdriver.Chrome("/opt/chromedriver", options=chrome_options)
        
        # Navegar a la página
        url = "https://ultimosismo.igp.gob.pe/ultimo-sismo/sismos-reportados"
        print(f"📡 Navegando a: {url}")
        driver.get(url)
        
        print("⏳ Esperando a que cargue la tabla de sismos...")
        
        # Esperar a que la tabla se cargue
        wait = WebDriverWait(driver, 20)
        tabla = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        print("✅ Tabla encontrada, extrayendo datos...")
        
        # Extraer datos de la tabla
        sismos = []
        filas = tabla.find_elements(By.TAG_NAME, "tr")[1:11]  # Saltar header y tomar 10 primeros
        
        print(f"📊 Encontradas {len(filas)} filas de sismos")
        
        for i, fila in enumerate(filas):
            try:
                celdas = fila.find_elements(By.TAG_NAME, "td")
                
                if len(celdas) >= 5:
                    sismo = {
                        'id': str(uuid.uuid4()),
                        'numero_reporte': celdas[0].text.strip(),
                        'referencia': celdas[1].text.strip(),
                        'fecha_hora': celdas[2].text.strip(),
                        'magnitud': celdas[3].text.strip(),
                        'timestamp_extraccion': datetime.now().isoformat(),
                        'orden': i + 1
                    }
                    sismos.append(sismo)
                    print(f"✅ Sismo {i+1}: {sismo['referencia']} - Magnitud: {sismo['magnitud']}")
                    
            except Exception as e:
                print(f"❌ Error procesando fila {i}: {e}")
                continue
        
        driver.quit()
        print("🔚 Navegador cerrado")
        
        # Guardar en DynamoDB
        if sismos:
            dynamodb = boto3.resource('dynamodb')
            tabla_db = dynamodb.Table('RimacFans')
            
            print("💾 Guardando en DynamoDB...")
            for sismo in sismos:
                try:
                    tabla_db.put_item(Item=sismo)
                    print(f"💾 Guardado: {sismo['numero_reporte']}")
                except Exception as e:
                    print(f"❌ Error guardando en DB: {e}")
        
        print(f"🎉 Extracción completada: {len(sismos)} sismos procesados")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f'Se extrajeron {len(sismos)} sismos exitosamente',
                'sismos_count': len(sismos),
                'sismos': sismos
            })
        }
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'message': 'Error en el proceso de scraping'
            })
        }