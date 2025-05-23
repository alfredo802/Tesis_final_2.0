import os
import shutil
import logging
import time
from datetime import datetime
import pandas as pd
import numpy as np

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analisis_completo.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def procesar_datos_para_pronosticos():
    """Procesa los datos para el análisis de pronósticos"""
    try:
        # Cargar datos originales
        df = pd.read_csv('valpoall.txt', sep='\s+', header=None, 
                        names=['año', 'mes', 'día', 'hora', 'keller', 'vega', 
                              'temp_aire', 'presion', 'humedad', 'temp_agua'])
        
        # Convertir columnas a tipos numéricos
        columnas_numericas = ['keller', 'vega', 'temp_aire', 'presion', 'humedad', 'temp_agua']
        for col in columnas_numericas:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Crear columna de fecha
        df['fecha'] = pd.to_datetime({
            'year': df['año'],
            'month': df['mes'],
            'day': df['día'],
            'hour': df['hora']
        })
        
        # Calcular promedios diarios
        df_diario = df.groupby(df['fecha'].dt.date)[columnas_numericas].mean().reset_index()
        
        # Guardar datos procesados
        os.makedirs('datos_procesados', exist_ok=True)
        df_diario.to_csv('datos_procesados/datos_procesados.csv', index=False)
        
        logging.info(f"Datos procesados guardados en datos_procesados/datos_procesados.csv")
        logging.info(f"Registros procesados: {len(df_diario)}")
        
        return True
    except Exception as e:
        logging.error(f"Error al procesar datos: {str(e)}")
        return False

def generar_reporte_individual(nombre_rutina, estado, detalles=""):
    """Genera un reporte individual para cada rutina"""
    reporte_path = f'reportes/reporte_{nombre_rutina}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    os.makedirs('reportes', exist_ok=True)
    
    with open(reporte_path, 'w', encoding='utf-8') as f:
        f.write(f"=== REPORTE DE {nombre_rutina.upper()} ===\n")
        f.write(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Estado: {estado}\n")
        f.write(f"Detalles:\n{detalles}\n")
    
    return reporte_path

def ejecutar_analisis_completo():
    # Crear directorios necesarios
    for dir_name in ['resultados', 'reportes', 'database', 'datos_procesados']:
        os.makedirs(dir_name, exist_ok=True)
    
    start_time = time.time()
    logging.info(f"Iniciando ejecución completa: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("=" * 50)
    
    # 1. Análisis básico de sensores
    logging.info("INICIANDO ANÁLISIS BÁSICO DE SENSORES")
    logging.info("=" * 50)
    try:
        import rutina_sensores
        detalles_sensores = rutina_sensores.main()
        reporte_sensores = generar_reporte_individual(
            "sensores",
            "EXITOSO",
            detalles_sensores
        )
        logging.info(f"[OK] Análisis básico de sensores completado exitosamente. Reporte generado: {reporte_sensores}")
    except Exception as e:
        error_msg = f"Error en análisis básico: {str(e)}"
        generar_reporte_individual("sensores", "ERROR", error_msg)
        logging.error(f"[ERROR] {error_msg}")
    
    # 2. Control de calidad
    logging.info("=" * 50)
    logging.info("INICIANDO CONTROL DE CALIDAD")
    logging.info("=" * 50)
    try:
        if not os.path.exists('valpoall.txt'):
            if os.path.exists('datos/valpoall.txt'):
                shutil.copy2('datos/valpoall.txt', 'valpoall.txt')
            else:
                raise FileNotFoundError("Archivo valpoall.txt no encontrado")
        
        import control_calidad
        detalles_calidad = control_calidad.main()
        reporte_calidad = generar_reporte_individual(
            "control_calidad",
            "EXITOSO",
            detalles_calidad
        )
        logging.info(f"[OK] Control de calidad completado exitosamente. Reporte generado: {reporte_calidad}")
    except Exception as e:
        error_msg = f"Error en control_calidad: {str(e)}"
        generar_reporte_individual("control_calidad", "ERROR", error_msg)
        logging.error(f"[ERROR] {error_msg}")
    
    # 3. Análisis de pronósticos
    logging.info("=" * 50)
    logging.info("INICIANDO ANÁLISIS DE PRONÓSTICOS")
    logging.info("=" * 50)
    try:
        # Procesar datos para pronósticos
        logging.info("Procesando datos para pronósticos...")
        if not procesar_datos_para_pronosticos():
            raise Exception("Error al procesar datos para pronósticos")
        
        import scripts.pronostico_sensores as pronostico
        detalles_pronostico = pronostico.main()
        reporte_pronostico = generar_reporte_individual(
            "pronosticos",
            "EXITOSO",
            detalles_pronostico
        )
        logging.info(f"[OK] Análisis de pronósticos completado exitosamente. Reporte generado: {reporte_pronostico}")
    except Exception as e:
        error_msg = f"Error en el análisis de pronósticos: {str(e)}"
        generar_reporte_individual("pronosticos", "ERROR", error_msg)
        logging.error(f"[ERROR] {error_msg}")
    
    # Resumen final
    end_time = time.time()
    logging.info("=" * 50)
    logging.info("RESUMEN DE EJECUCIÓN")
    logging.info("=" * 50)
    logging.info(f"Tiempo total de ejecución: {end_time - start_time:.2f} segundos")
    
    # Verificar resultados
    rutina_ok = any([
        os.path.exists('resultados/graficos_sensores.png'),
        os.path.exists('resultados/todos_sensores_combinado.png'),
        os.path.exists('resultados/matriz_correlacion.png')
    ])
    
    control_ok = any([
        os.path.exists('resultados/Control_Calidad.png'),
        os.path.exists('resultados/control_calidad.png'),
        os.path.exists('resultados/correlacion_sensores.png'),
        os.path.exists('resultados/control_sensor_keller.png'),
        os.path.exists('resultados/control_sensor_vega.png')
    ])
    
    pronostico_ok = any([
        os.path.exists('resultados/pronostico_keller.png'),
        os.path.exists('resultados/pronostico_vega.png'),
        os.path.exists('resultados/pronostico_presion.png'),
        os.path.exists('resultados/pronostico_temp_aire.png'),
        os.path.exists('resultados/pronostico_temp_agua.png'),
        os.path.exists('resultados/pronostico_humedad.png')
    ])
    
    # Generar reporte final
    resumen_final = f"""
Estado de las rutinas:
- rutina_sensores: {'OK' if rutina_ok else 'ERROR'}
- control_calidad: {'OK' if control_ok else 'ERROR'}
- pronosticos: {'OK' if pronostico_ok else 'ERROR'}

Tiempo total de ejecución: {end_time - start_time:.2f} segundos
"""
    
    reporte_final = generar_reporte_individual(
        "resumen_final",
        "COMPLETADO" if all([rutina_ok, control_ok, pronostico_ok]) else "CON ERRORES",
        resumen_final
    )
    
    logging.info(f"Reporte final generado: {reporte_final}")
    
    if not all([rutina_ok, control_ok, pronostico_ok]):
        logging.error("\n[ERROR] Algunos análisis fallaron")
    else:
        logging.info("\n[OK] Todos los análisis se completaron exitosamente")

if __name__ == "__main__":
    ejecutar_analisis_completo() 