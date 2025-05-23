import os
import time
import logging
from datetime import datetime
import rutina_sensores
import control_calidad
import ejecutar_analisis_completo
import glob

# Configurar logging
def setup_logging(rutina_name):
    # Crear directorio de reportes si no existe
    if not os.path.exists('reportes'):
        os.makedirs('reportes')
    
    # Configurar el archivo de log
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f'reportes/{rutina_name}_{timestamp}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger()

def ejecutar_rutina(rutina_name, rutina_func):
    """Ejecuta una rutina y registra su tiempo de ejecución y resultados"""
    logger = setup_logging(rutina_name)
    logger.info(f"Iniciando ejecución de {rutina_name}")
    
    start_time = time.time()
    try:
        # Ejecutar la rutina
        resultado = rutina_func()
        
        # Calcular tiempo de ejecución
        execution_time = time.time() - start_time
        
        # Registrar resultados
        logger.info(f"Rutina {rutina_name} completada exitosamente")
        logger.info(f"Tiempo de ejecución: {execution_time:.2f} segundos")
        
        if resultado:
            logger.info("Resultados del análisis:")
            logger.info(resultado)
        
        return True, execution_time, resultado
    
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error en la rutina {rutina_name}: {str(e)}")
        return False, execution_time, str(e)

def limpiar_reportes(tipo):
    archivos = glob.glob(f'reportes/reporte_{tipo}_*.txt')
    if len(archivos) > 2:
        archivos.sort(key=os.path.getmtime, reverse=True)
        for archivo in archivos[2:]:
            try:
                os.remove(archivo)
            except Exception:
                pass

def main():
    """Función principal que ejecuta todas las rutinas en secuencia"""
    try:
        # Crear directorio de reportes si no existe
        if not os.path.exists('reportes'):
            os.makedirs('reportes')
        
        # Ejecutar rutina de sensores
        print("Iniciando ejecución de Rutina de Sensores")
        inicio = time.time()
        resultado = rutina_sensores.main()
        tiempo = time.time() - inicio
        print(f"Rutina Rutina de Sensores completada exitosamente")
        print(f"Tiempo de ejecución: {tiempo:.2f} segundos")
        print(f"Resultados del análisis:\n{resultado}")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path_sensores = f'reportes/reporte_sensores_{timestamp}.txt'
        with open(path_sensores, 'w', encoding='utf-8') as f:
            f.write(f"Reporte de Sensores - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")
            f.write(resultado)
        limpiar_reportes('sensores')
        
        # Ejecutar control de calidad
        print("\nIniciando ejecución de Control de Calidad")
        inicio = time.time()
        resultado = control_calidad.main()
        tiempo = time.time() - inicio
        print(f"Rutina Control de Calidad completada exitosamente")
        print(f"Tiempo de ejecución: {tiempo:.2f} segundos")
        print(f"Resultados del análisis:\n{resultado}")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path_control = f'reportes/reporte_control_calidad_{timestamp}.txt'
        with open(path_control, 'w', encoding='utf-8') as f:
            f.write(f"Reporte de Control de Calidad - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")
            f.write(resultado)
        limpiar_reportes('control_calidad')
        
        # Ejecutar análisis completo
        print("\nIniciando ejecución de Análisis Completo")
        inicio = time.time()
        resultado = ejecutar_analisis_completo.ejecutar_analisis_completo()
        tiempo = time.time() - inicio
        print(f"Rutina Análisis Completo completada exitosamente")
        print(f"Tiempo de ejecución: {tiempo:.2f} segundos")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path_pronosticos = f'reportes/reporte_pronosticos_{timestamp}.txt'
        with open(path_pronosticos, 'w', encoding='utf-8') as f:
            f.write(f"Reporte de Pronósticos - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")
            f.write(resultado)
        limpiar_reportes('pronosticos')
        
        # Generar reporte final
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path_final = f'reportes/reporte_final_{timestamp}.txt'
        with open(path_final, 'w', encoding='utf-8') as f:
            f.write(f"Reporte Final - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")
            f.write(f"Tiempo total de ejecución: {tiempo:.2f} segundos\n")
            f.write(f"Estado: [OK] Todos los análisis se completaron exitosamente\n")
        limpiar_reportes('final')
        return True
    except Exception as e:
        print(f"Error en la ejecución: {str(e)}")
        return False

if __name__ == "__main__":
    main() 