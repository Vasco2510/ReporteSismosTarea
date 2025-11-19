from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_selenium_connection():
    # Configurar opciones de Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar en modo sin interfaz gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        # Inicializar el driver de Chrome
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navegar a la página
        url = "https://ultimosismo.igp.gob.pe/ultimo-sismo/sismos-reportados"
        driver.get(url)
        
        print("Página cargada, esperando a que se renderice el contenido...")
        
        # Esperar a que algún elemento específico de la tabla esté presente
        wait = WebDriverWait(driver, 10)
        
        # Esperar a que la tabla o algún elemento de contenido se cargue
        try:
            # Buscar el título principal de la página
            titulo = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "h2"))
            )
            print(f"Título encontrado: {titulo.text}")
            
            # Buscar la tabla de sismos
            tabla = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            print("✅ Tabla de sismos encontrada!")
            
            # Contar las filas de la tabla
            filas = tabla.find_elements(By.TAG_NAME, "tr")
            print(f"Número de filas en la tabla: {len(filas)}")
            
            # Mostrar las primeras filas como prueba
            for i, fila in enumerate(filas[:11]):
                print(f"Fila {i}: {fila.text[:100]}...")  # Mostrar primeros 100 caracteres
            
            return True
            
        except Exception as e:
            print(f"Error al encontrar elementos: {e}")
            # Tomar screenshot para debug
            driver.save_screenshot("debug_page.png")
            print("Screenshot guardado como 'debug_page.png'")
            return False
            
    except Exception as e:
        print(f"Error con Selenium: {e}")
        return False
    finally:
        # Cerrar el navegador
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    print("Probando conexión con Selenium...")
    success = test_selenium_connection()
    
    if success:
        print("\n✅ Selenium funciona! Podemos extraer los datos de los sismos.")
    else:
        print("\n❌ Hubo problemas con Selenium.")