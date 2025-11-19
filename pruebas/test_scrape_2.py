# scrape_sismos_local.py
import json
import boto3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import uuid
from datetime import datetime

def test_scraping_local():
    try:
        # Configurar Chrome para ejecución local
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navegar a la página
        url = "https://ultimosismo.igp.gob.pe/ultimo-sismo/sismos-reportados"
        driver.get(url)
        
        print("Página cargada, esperando tabla de sismos...")
        
        # Esperar a que la tabla se cargue
        wait = WebDriverWait(driver, 15)
        tabla = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        print("✅ Tabla encontrada, extrayendo datos...")
        
        # Extraer datos de la tabla
        sismos = []
        filas = tabla.find_elements(By.TAG_NAME, "tr")[1:11]  # Saltar header y tomar 10 primeros
        
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
        
        # Mostrar resultados (sin guardar en DynamoDB por ahora)
        print(f"\n🎉 Extracción completada: {len(sismos)} sismos encontrados")
        
        for sismo in sismos:
            print(f"📊 {sismo['numero_reporte']}: {sismo['referencia']} - Mag: {sismo['magnitud']}")
        
        return sismos
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        return []

if __name__ == "__main__":
    print("🚀 Iniciando prueba local de scraping...")
    sismos = test_scraping_local()
    
    if sismos:
        print(f"\n✅ ¡Prueba exitosa! Se extrajeron {len(sismos)} sismos")
        print("📝 Puedes proceder con el despliegue en AWS")
    else:
        print("\n❌ La prueba falló, revisa los errores arriba")