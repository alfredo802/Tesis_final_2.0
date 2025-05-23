# PredictMareas – Sistema de Monitoreo y Pronóstico de Mareas para Valparaíso

PredictMareas es una plataforma web integral para el monitoreo, análisis y pronóstico de mareas en Valparaíso, Chile. El sistema automatiza el procesamiento de datos, control de calidad, generación de reportes y visualización interactiva, facilitando la toma de decisiones y la gestión de alertas.

---

## Tabla de Contenidos
- [Características Principales](#características-principales)
- [Instalación y Configuración](#instalación-y-configuración)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Ejecución](#ejecución)
- [Rutinas y Reportes Automáticos](#rutinas-y-reportes-automáticos)
- [Funcionalidades Web](#funcionalidades-web)
- [Ejemplo de Resultados y Reportes](#ejemplo-de-resultados-y-reportes)
- [Seguridad y Notas](#seguridad-y-notas)
- [Solución de Problemas](#solución-de-problemas)
- [Contribución](#contribución)
- [Licencia](#licencia)
- [Contacto](#contacto)

---

## Características Principales
- **Pronóstico de mareas en tiempo real** con modelo Random Forest validado (R² = 0.82).
- **Alertas automáticas** para mareas altas (>1.70m).
- **Control de calidad de sensores**: detección de datos faltantes, outliers y correlación entre sensores.
- **Generación automática de reportes** (sensores, control de calidad, pronósticos, alertas).
- **Visualización web**: gráficos interactivos, mapas y panel de administración.
- **Historial y descarga de reportes** desde la web y el panel admin.

---

## Instalación y Configuración

### Requisitos
- Python 3.8 o superior
- pip
- Navegador web moderno

### Pasos
1. **Clona el repositorio y entra al directorio:**
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd [NOMBRE_DEL_DIRECTORIO]
   ```
2. **Crea y activa un entorno virtual (opcional pero recomendado):**
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```
3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configura la clave de Google Maps:**
   - Crea un archivo `config.py` en la raíz con:
     ```python
     GOOGLE_MAPS_API_KEY = 'AIzaSyCLZHCoAoHfgJWwGJkFqextPFyji8147Ig'
     ```
   - Obtén la clave en [Google Cloud Console](https://console.cloud.google.com/)

---

## Estructura del Proyecto

```
proyecto/
│
├── app.py                      # Servidor principal Flask
├── ejecutar_rutinas.py         # Orquestador de rutinas
├── control_calidad.py          # Rutina de control de calidad
├── rutina_sensores.py          # Procesamiento de sensores
├── ejecutar_analisis_completo.py # Ejecución de análisis completo
├── config.py                   # Claves y configuración
├── requirements.txt            # Dependencias
├── static/                     # JS, CSS, imágenes
│   ├── css/style.css
│   └── js/main.js
├── templates/                  # HTML (index, admin, login)
├── reportes/                   # Reportes automáticos (TXT)
├── resultados/                 # Imágenes y archivos de resultados
├── datos_procesados/           # CSV procesados
├── database/                   # Base de datos y auxiliares
├── scripts/                    # Scripts auxiliares
├── datos/                      # Datos crudos
└── README.md                   # Este archivo
```

---

## Ejecución

1. Activa el entorno virtual si corresponde.
2. Ejecuta la aplicación:
   ```bash
   python app.py
   ```
3. Abre tu navegador en:
   ```
   http://localhost:5000
   ```

---

## Rutinas y Reportes Automáticos

- **Rutina de Sensores:** Procesa datos crudos, genera gráficos y correlaciones.
- **Rutina de Control de Calidad:** Analiza datos faltantes, outliers y control estadístico.
- **Rutina de Pronóstico:** Genera pronósticos y alertas automáticas.
- **Ejecución completa:** `ejecutar_analisis_completo.py` ejecuta todas las rutinas en secuencia.
- **Reportes generados:**
  - `reporte_sensores_YYYYMMDD_HHMMSS.txt`
  - `reporte_control_calidad_YYYYMMDD_HHMMSS.txt`
  - `reporte_pronosticos_YYYYMMDD_HHMMSS.txt`
  - `reporte_ultimas_alertas_YYYYMMDD_HHMMSS.txt` (últimas 4 alertas)
  - `historial_alertas.txt` (historial completo)
  - Imágenes y gráficos en `/resultados/`

---

## Funcionalidades Web

### Usuario
- Consulta de pronóstico por rango de fechas o para el día actual.
- Visualización de gráfico de mareas y mapa interactivo.
- Visualización de alertas de mareas altas.
- Acceso a reportes automáticos (sensores, control de calidad, pronósticos, alertas).

### Panel de Administración
- Login seguro (usuario: `admin`, contraseña: `admin123`).
- Descarga de reportes e imágenes generadas.
- Visualización y descarga del historial de alertas.
- Gráfica de días con alerta de marea alta.
- Historial de consultas y visitas.

---

## Ejemplo de Resultados y Reportes

- **Modelo Random Forest** entrenado con datos hasta mayo 2025 (R² = 0.82).
- **Alertas automáticas**: Nueva alerta para mareas > 1.70m implementada.
- **Control de Calidad de Sensores:**
  - Datos faltantes: keller: 161 (1.69%), vega: 164 (1.72%), temp_aire: 163 (1.71%), presion: 164 (1.72%), humedad: 162 (1.70%), temp_agua: 164 (1.72%)
  - Valores extremos detectados: keller: 3, vega: 0, temp_aire: 40, presion: 310, humedad: 70, temp_agua: 1
  - Correlación entre sensores: r = 0.9985, R² = 0.9970
- **Estadísticas de control:**
  - Sensor Keller: Media 2.987m, UCL 4.679m, LCL 1.295m
  - Sensor Vega: Media 4.857m, UCL 6.509m, LCL 3.204m
- **Archivos generados:**
  - Gráficos: Control_Calidad.png, Correlacion_Sensores.png, Graficos_Control_Sensores.png
  - Reportes: TXT en `/reportes/`, CSV en `/datos_procesados/`

---

## Seguridad y Notas
- El sistema está en modo desarrollo. **No usar en producción sin ajustes de seguridad.**
- Cambia la clave secreta y las credenciales de admin antes de desplegar en producción.
- La clave de Google Maps debe estar correctamente configurada en `config.py`.
- Para soporte o reporte de errores, contactar al equipo de desarrollo.

---

## Solución de Problemas

- **Error de conexión a la API de Google Maps:**
  - Verifica la clave API y que la API esté habilitada en Google Cloud Console.
- **No se cargan los datos:**
  - Verifica que los archivos de pronóstico estén en la carpeta `resultados/`.
- **Error en la aplicación:**
  - Revisa los logs en la consola y que todas las dependencias estén instaladas.

---

## Contribución

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/NuevaFeature`)
3. Commit a tus cambios (`git commit -m 'Agrega NuevaFeature'`)
4. Push a la rama (`git push origin feature/NuevaFeature`)
5. Abre un Pull Request

---

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## Contacto

Equipo de desarrollo PredictMareas

Alfredo Herrera Figueroa - a.herrerafigueroa@uandresbello.edu

Link del Proyecto: [https://github.com/alfredo802/Tesis_final_2.0](https://github.com/alfredo802/Tesis_final_2.0) 