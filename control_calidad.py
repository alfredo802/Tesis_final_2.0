import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Configurar backend no interactivo
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def cargar_datos(archivo):
    """Carga los datos del archivo y los convierte a DataFrame"""
    try:
        data = np.loadtxt(archivo)
        df = pd.DataFrame({
            'año': data[:, 0].astype(int),
            'mes': data[:, 1].astype(int),
            'día': data[:, 2].astype(int),
            'hora': data[:, 3].astype(int),
            'keller': data[:, 4],
            'vega': data[:, 5],
            'temp_aire': data[:, 6],
            'presion': data[:, 7],
            'humedad': data[:, 8],
            'temp_agua': data[:, 9]
        })
        
        # Crear fechas manualmente
        fechas = []
        for _, row in df.iterrows():
            try:
                fecha = datetime(
                    year=int(row['año']),
                    month=int(row['mes']),
                    day=int(row['día']),
                    hour=int(row['hora'])
                )
                fechas.append(fecha)
            except ValueError as e:
                print(f"Error en fecha: {row['año']}-{row['mes']}-{row['día']} {row['hora']}:00")
                fechas.append(pd.NaT)
        
        df['fecha'] = fechas
        return df
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        return None

def analizar_datos_faltantes(df):
    """Analiza y reporta datos faltantes"""
    faltantes = df.isnull().sum()
    porcentaje_faltantes = (faltantes / len(df)) * 100
    
    print("\n=== ANÁLISIS DE DATOS FALTANTES ===")
    for col in df.columns:
        if faltantes[col] > 0:
            print(f"{col}: {faltantes[col]} datos faltantes ({porcentaje_faltantes[col]:.2f}%)")

def analizar_valores_extremos(df):
    """Analiza valores extremos usando el método IQR"""
    print("\n=== ANÁLISIS DE VALORES EXTREMOS ===")
    
    sensores = ['keller', 'vega', 'temp_aire', 'presion', 'humedad', 'temp_agua']
    for sensor in sensores:
        Q1 = df[sensor].quantile(0.25)
        Q3 = df[sensor].quantile(0.75)
        IQR = Q3 - Q1
        
        limite_inferior = Q1 - 1.5 * IQR
        limite_superior = Q3 + 1.5 * IQR
        
        valores_extremos = df[(df[sensor] < limite_inferior) | (df[sensor] > limite_superior)][sensor]
        
        print(f"\n{sensor.upper()}:")
        print(f"Rango normal: [{limite_inferior:.2f}, {limite_superior:.2f}]")
        print(f"Valores extremos: {len(valores_extremos)}")
        if len(valores_extremos) > 0:
            print("Primeros 5 valores extremos:")
            print(valores_extremos.head())

def calcular_error_sensores(df):
    """Calcula el error entre los sensores de marea"""
    print("\n=== ANÁLISIS DE ERROR ENTRE SENSORES DE MAREA ===")
    
    # Calcular diferencia entre sensores
    df['diferencia'] = df['keller'] - df['vega']
    
    # Estadísticas de la diferencia
    print("\nEstadísticas de la diferencia Keller - Vega:")
    print(f"Media: {df['diferencia'].mean():.3f} m")
    print(f"Desviación estándar: {df['diferencia'].std():.3f} m")
    print(f"Máximo: {df['diferencia'].max():.3f} m")
    print(f"Mínimo: {df['diferencia'].min():.3f} m")
    
    # Calcular RMSE
    rmse = np.sqrt(np.mean(df['diferencia']**2))
    print(f"RMSE: {rmse:.3f} m")

def analizar_correlacion(df):
    """Analiza la correlación entre los sensores Vega y Keller"""
    print("\n=== ANÁLISIS DE CORRELACIÓN ENTRE SENSORES ===")
    
    # Eliminar filas donde falten datos en cualquiera de los sensores
    df_clean = df.dropna(subset=['keller', 'vega'])
    
    # Calcular correlación
    corr = df_clean['keller'].corr(df_clean['vega'])
    r_squared = corr ** 2
    
    # Realizar regresión lineal
    slope, intercept, r_value, p_value, std_err = stats.linregress(df_clean['keller'], df_clean['vega'])
    
    print(f"\nCoeficiente de correlación (r): {corr:.4f}")
    print(f"Coeficiente de determinación (R²): {r_squared:.4f}")
    print(f"Pendiente de la regresión: {slope:.4f}")
    print(f"Intercepto: {intercept:.4f}")
    print(f"Error estándar: {std_err:.4f}")
    
    # Crear gráfico de correlación
    plt.figure(figsize=(10, 8))
    plt.scatter(df_clean['keller'], df_clean['vega'], alpha=0.5)
    
    # Añadir línea de regresión
    x = np.array([df_clean['keller'].min(), df_clean['keller'].max()])
    y = slope * x + intercept
    plt.plot(x, y, 'r', label=f'y = {slope:.4f}x + {intercept:.4f}')
    
    plt.xlabel('Sensor Keller (m)')
    plt.ylabel('Sensor Vega (m)')
    plt.title('Correlación entre Sensores Keller y Vega')
    plt.grid(True)
    plt.legend()
    
    # Añadir texto con estadísticas
    plt.text(0.05, 0.95, f'R² = {r_squared:.4f}\nr = {corr:.4f}', 
             transform=plt.gca().transAxes, 
             bbox=dict(facecolor='white', alpha=0.8))
    
    plt.savefig('Correlacion_Sensores.png')
    plt.close()

def generar_graficos_control(df):
    """Genera gráficos de control de calidad"""
    try:
        # Crear figura con backend Agg
        plt.switch_backend('Agg')
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        fig.suptitle('Control de Calidad de Datos', fontsize=16)
        
        # Gráfico de diferencias entre sensores
        axes[0,0].plot(df['fecha'], df['diferencia'])
        axes[0,0].set_title('Diferencia Keller - Vega')
        axes[0,0].set_ylabel('Diferencia (m)')
        axes[0,0].grid(True)
        
        # Histograma de diferencias
        axes[0,1].hist(df['diferencia'], bins=50)
        axes[0,1].set_title('Distribución de Diferencias')
        axes[0,1].set_xlabel('Diferencia (m)')
        axes[0,1].grid(True)
        
        # Boxplot de sensores
        axes[1,0].boxplot([df['keller'], df['vega']], labels=['Keller', 'Vega'])
        axes[1,0].set_title('Boxplot Sensores de Marea')
        axes[1,0].set_ylabel('Altura (m)')
        axes[1,0].grid(True)
        
        # Gráfico de dispersión
        axes[1,1].scatter(df['keller'], df['vega'], alpha=0.5)
        axes[1,1].set_title('Keller vs Vega')
        axes[1,1].set_xlabel('Keller (m)')
        axes[1,1].set_ylabel('Vega (m)')
        axes[1,1].grid(True)
        
        # Gráfico de temperatura
        axes[2,0].plot(df['fecha'], df['temp_aire'], label='Aire')
        axes[2,0].plot(df['fecha'], df['temp_agua'], label='Agua')
        axes[2,0].set_title('Temperaturas')
        axes[2,0].set_ylabel('Temperatura (°C)')
        axes[2,0].legend()
        axes[2,0].grid(True)
        
        # Gráfico de presión y humedad
        ax2 = axes[2,1].twinx()
        axes[2,1].plot(df['fecha'], df['presion'], 'b-', label='Presión')
        ax2.plot(df['fecha'], df['humedad'], 'r-', label='Humedad')
        axes[2,1].set_title('Presión y Humedad')
        axes[2,1].set_ylabel('Presión (mbar)')
        ax2.set_ylabel('Humedad (%)')
        axes[2,1].legend(loc='upper left')
        ax2.legend(loc='upper right')
        axes[2,1].grid(True)
        
        plt.tight_layout()
        plt.savefig('Control_Calidad.png')
        plt.close()
    except Exception as e:
        print(f"Error al generar gráficos de control: {e}")

def generar_graficos_control_sensores(df):
    """Genera gráficos de control para los sensores Vega y Keller"""
    print("\n=== GENERANDO GRÁFICOS DE CONTROL ===")
    
    # Eliminar filas donde falten datos en cualquiera de los sensores
    df_clean = df.dropna(subset=['keller', 'vega'])
    
    # Configurar subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
    fig.suptitle('Gráficos de Control de Sensores', fontsize=16)
    
    # Calcular límites de control para Keller
    keller_mean = df_clean['keller'].mean()
    keller_std = df_clean['keller'].std()
    keller_ucl = keller_mean + 3 * keller_std
    keller_lcl = keller_mean - 3 * keller_std
    
    # Gráfico de control para Keller
    ax1.plot(df_clean['fecha'], df_clean['keller'], 'b-', label='Mediciones', alpha=0.6)
    ax1.axhline(y=keller_mean, color='g', linestyle='-', label='Media')
    ax1.axhline(y=keller_ucl, color='r', linestyle='--', label='UCL/LCL (±3σ)')
    ax1.axhline(y=keller_lcl, color='r', linestyle='--')
    ax1.set_title('Gráfico de Control - Sensor Keller')
    ax1.set_ylabel('Altura (m)')
    ax1.grid(True)
    ax1.legend()
    
    # Calcular límites de control para Vega
    vega_mean = df_clean['vega'].mean()
    vega_std = df_clean['vega'].std()
    vega_ucl = vega_mean + 3 * vega_std
    vega_lcl = vega_mean - 3 * vega_std
    
    # Gráfico de control para Vega
    ax2.plot(df_clean['fecha'], df_clean['vega'], 'b-', label='Mediciones', alpha=0.6)
    ax2.axhline(y=vega_mean, color='g', linestyle='-', label='Media')
    ax2.axhline(y=vega_ucl, color='r', linestyle='--', label='UCL/LCL (±3σ)')
    ax2.axhline(y=vega_lcl, color='r', linestyle='--')
    ax2.set_title('Gráfico de Control - Sensor Vega')
    ax2.set_ylabel('Altura (m)')
    ax2.set_xlabel('Fecha')
    ax2.grid(True)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('Graficos_Control_Sensores.png')
    plt.close()
    
    # Imprimir estadísticas de control
    print("\nEstadísticas de Control - Sensor Keller:")
    print(f"Media: {keller_mean:.3f} m")
    print(f"Desviación estándar: {keller_std:.3f} m")
    print(f"Límite superior de control (UCL): {keller_ucl:.3f} m")
    print(f"Límite inferior de control (LCL): {keller_lcl:.3f} m")
    
    print("\nEstadísticas de Control - Sensor Vega:")
    print(f"Media: {vega_mean:.3f} m")
    print(f"Desviación estándar: {vega_std:.3f} m")
    print(f"Límite superior de control (UCL): {vega_ucl:.3f} m")
    print(f"Límite inferior de control (LCL): {vega_lcl:.3f} m")

def main():
    """
    Función principal que ejecuta el control de calidad
    Retorna un string con los detalles del análisis
    """
    detalles = []
    
    print("Cargando datos de valpoall.txt...")
    detalles.append("Cargando datos de valpoall.txt...")
    
    # Cargar datos
    df = cargar_datos('valpoall.txt')
    
    # Realizar análisis
    analizar_datos_faltantes(df)
    analizar_valores_extremos(df)
    calcular_error_sensores(df)
    analizar_correlacion(df)
    
    # Generar gráficos
    print("\nGenerando gráficos de control de calidad...")
    generar_graficos_control(df)
    generar_graficos_control_sensores(df)
    
    detalles.append("\nAnálisis completado. Se han generado los siguientes archivos:")
    detalles.append("- Control_Calidad.png")
    detalles.append("- Correlacion_Sensores.png")
    detalles.append("- Graficos_Control_Sensores.png")
    
    return "\n".join(detalles)

if __name__ == "__main__":
    main() 