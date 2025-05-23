import matplotlib
matplotlib.use('Agg')  # Configurar backend no interactivo
from flask import Flask, render_template, jsonify, request, send_file, redirect, url_for, session, flash, send_from_directory
import pandas as pd
import json
from datetime import datetime, timedelta
import os
from config import GOOGLE_MAPS_API_KEY
import ejecutar_rutinas
import glob
import csv

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Cambia esto en producción

# Contador global para las consultas
contador_consultas = 0
ULTIMA_EJECUCION = None

ADMIN_USER = 'admin'
ADMIN_PASS = 'admin123'

def cargar_pronostico_marea():
    try:
        df = pd.read_csv('resultados/pronostico_keller_futuro.csv')
        df['fecha'] = pd.to_datetime(df['fecha'])
        return df
    except Exception as e:
        print(f"Error al cargar datos: {str(e)}")
        return None

def obtener_ultimos_reportes():
    """Obtiene los reportes más recientes de cada tipo que tengan contenido"""
    reportes = {
        'sensores': None,
        'control_calidad': None,
        'pronosticos': None,
        'final': None,
        'alertas': None
    }
    for tipo in ['sensores', 'control_calidad', 'pronosticos', 'final']:
        archivos = glob.glob(f'reportes/reporte_{tipo}_*.txt')
        if archivos:
            archivos.sort(key=os.path.getmtime, reverse=True)
            for archivo in archivos:
                try:
                    if os.path.getsize(archivo) > 0:
                        reportes[tipo] = archivo
                        break
                except Exception:
                    continue
    # Buscar el reporte de alertas
    archivos_alertas = glob.glob('reportes/reporte_ultimas_alertas_*.txt')
    if archivos_alertas:
        archivos_alertas.sort(key=os.path.getmtime, reverse=True)
        for archivo in archivos_alertas:
            try:
                if os.path.getsize(archivo) > 0:
                    reportes['alertas'] = archivo
                    break
            except Exception:
                continue
    return reportes

def ejecutar_rutinas_si_es_necesario():
    """Ejecuta las rutinas solo si han pasado 25 consultas o es la primera vez"""
    global contador_consultas, ULTIMA_EJECUCION
    
    contador_consultas += 1
    
    # Ejecutar si es la primera vez o han pasado 25 consultas
    if ULTIMA_EJECUCION is None or contador_consultas >= 25:
        ejecutar_rutinas.main()
        contador_consultas = 0
        ULTIMA_EJECUCION = datetime.now()
        return True
    return False

def registrar_historial_consulta(ip):
    with open('historial_consultas.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%H:%M:%S'), ip])

@app.route('/')
def index():
    # Verificar si es necesario ejecutar las rutinas
    ejecutar_rutinas_si_es_necesario()
    # Generar el reporte de alertas automáticamente
    generar_reporte_ultimas_alertas()
    reportes = obtener_ultimos_reportes()
    print(f"Clave de Google Maps: {GOOGLE_MAPS_API_KEY}")  # Debug print
    return render_template('index.html', 
                         google_maps_api_key=GOOGLE_MAPS_API_KEY,
                         reportes=reportes)

@app.route('/api/pronostico')
def get_pronostico():
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    registrar_historial_consulta(request.remote_addr)
    ejecutar_rutinas_si_es_necesario()
    df = cargar_pronostico_marea()
    if df is None:
        return jsonify({'error': 'No se pudieron cargar los datos'}), 500
    if fecha_inicio and fecha_fin:
        fecha_inicio = pd.to_datetime(fecha_inicio)
        fecha_fin = pd.to_datetime(fecha_fin)
        df = df[(df['fecha'] >= fecha_inicio) & (df['fecha'] <= fecha_fin)]
    # Convertir a formato para el gráfico
    datos = {
        'fechas': df['fecha'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
        'valores': df['keller_pronostico'].tolist()
    }
    # Solo mostrar alerta si la consulta es para el día actual
    alerta = None
    hoy = datetime.now().date()
    if fecha_inicio and fecha_fin and fecha_inicio.date() == fecha_fin.date() == hoy and not df.empty:
        idx_pleamar = df['keller_pronostico'].idxmax()
        pleamar_valor = df.loc[idx_pleamar, 'keller_pronostico']
        pleamar_fecha = df.loc[idx_pleamar, 'fecha'].strftime('%Y-%m-%d')
        if pleamar_valor > 1.70:
            alerta = f"Existe la probabilidad que se produzcan mareas fuera de lo normal para la zona el día {pleamar_fecha}, tener precaución."
        else:
            alerta = "Condición Normal"
    datos['alerta'] = alerta
    return jsonify(datos)

@app.route('/api/pronostico/hoy')
def get_pronostico_hoy():
    registrar_historial_consulta(request.remote_addr)
    
    # Verificar si es necesario ejecutar las rutinas
    ejecutar_rutinas_si_es_necesario()
    
    df = cargar_pronostico_marea()
    if df is None:
        return jsonify({'error': 'No se pudieron cargar los datos'}), 500
    
    hoy = datetime.now().date()
    df_hoy = df[df['fecha'].dt.date == hoy]
    
    datos = {
        'fechas': df_hoy['fecha'].dt.strftime('%H:%M').tolist(),
        'valores': df_hoy['keller_pronostico'].tolist()
    }
    
    return jsonify(datos)

@app.route('/api/reportes/<tipo>')
def obtener_reporte(tipo):
    """Endpoint para obtener el contenido de un reporte específico"""
    reportes = obtener_ultimos_reportes()
    if tipo in reportes and reportes[tipo]:
        try:
            with open(reportes[tipo], 'r', encoding='utf-8') as f:
                contenido = f.read()
            return jsonify({
                'contenido': contenido,
                'fecha': datetime.fromtimestamp(os.path.getmtime(reportes[tipo])).strftime('%Y-%m-%d %H:%M:%S')
            })
        except Exception as e:
            return jsonify({'error': f'Error al leer el reporte: {str(e)}'}), 500
    return jsonify({'error': 'Reporte no encontrado'}), 404

@app.route('/api/mareas_hoy')
def mareas_hoy():
    df = cargar_pronostico_marea()
    if df is None:
        return jsonify({'error': 'No se pudieron cargar los datos', 'alerta': None}), 500

    hoy = datetime.now().date()
    df_hoy = df[df['fecha'].dt.date == hoy]
    if df_hoy.empty:
        return jsonify({'error': 'No hay datos para hoy', 'alerta': None}), 404

    # Buscar pleamar (máximo) y bajamar (mínimo) del día
    idx_pleamar = df_hoy['keller_pronostico'].idxmax()
    idx_bajamar = df_hoy['keller_pronostico'].idxmin()
    pleamar = {
        'hora': df_hoy.loc[idx_pleamar, 'fecha'].strftime('%H:%M'),
        'valor': round(df_hoy.loc[idx_pleamar, 'keller_pronostico'], 2)
    }
    bajamar = {
        'hora': df_hoy.loc[idx_bajamar, 'fecha'].strftime('%H:%M'),
        'valor': round(df_hoy.loc[idx_bajamar, 'keller_pronostico'], 2)
    }

    alerta = None
    if pleamar['valor'] > 1.70:
        alerta = 'Existe la probabilidad que se produzcan mareas fuera de lo normal para la zona.'
    else:
        alerta = 'Condición Normal'

    return jsonify({
        'pleamar': pleamar,
        'bajamar': bajamar,
        'alerta': alerta
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/admin/imagenes')
def admin_imagenes():
    # Buscar imágenes en la carpeta resultados
    imagenes = []
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        imagenes.extend(glob.glob(os.path.join('resultados', ext)))
    imagenes = sorted(imagenes, key=os.path.getmtime, reverse=True)
    # Solo el nombre del archivo
    imagenes = [os.path.basename(img) for img in imagenes]
    return jsonify(imagenes)

@app.route('/admin/reportes')
def admin_reportes():
    # Buscar reportes en la carpeta reportes
    reportes = []
    for ext in ['*.txt']:
        reportes.extend(glob.glob(os.path.join('reportes', ext)))
    reportes = sorted(reportes, key=os.path.getmtime, reverse=True)
    # Solo el nombre y fecha
    reportes_info = [{
        'nombre': os.path.basename(rep),
        'fecha': datetime.fromtimestamp(os.path.getmtime(rep)).strftime('%Y-%m-%d %H:%M:%S')
    } for rep in reportes]
    return jsonify(reportes_info)

@app.route('/admin/historial_consultas')
def admin_historial_consultas():
    datos = []
    try:
        with open('historial_consultas.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 3:
                    datos.append({'fecha': row[0], 'hora': row[1], 'ip': row[2]})
    except FileNotFoundError:
        pass
    return jsonify(datos)

@app.route('/admin/descargar_log')
def descargar_log():
    log_path = 'analisis_completo.log'
    if os.path.exists(log_path):
        return send_file(log_path, as_attachment=True)
    else:
        return 'Archivo de log no encontrado', 404

@app.route('/admin/descargar_release_note')
def descargar_release_note():
    path = os.path.join('reportes', 'release_note.txt')
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return 'Archivo release_note.txt no encontrado', 404

@app.route('/admin/descargar_reporte/<nombre>')
def descargar_reporte(nombre):
    path = os.path.join('reportes', nombre)
    if os.path.exists(path) and nombre.endswith('.txt'):
        return send_file(path, as_attachment=True)
    else:
        return 'Reporte no encontrado', 404

@app.route('/resultados/<path:filename>')
def resultados_static(filename):
    return send_from_directory('resultados', filename)

# Nuevo endpoint para historial de alertas
@app.route('/admin/alertas')
def admin_alertas():
    df = cargar_pronostico_marea()
    if df is None:
        return jsonify([])
    df['fecha_dia'] = df['fecha'].dt.date
    alertas = []
    for fecha, grupo in df.groupby('fecha_dia'):
        max_valor = grupo['keller_pronostico'].max()
        if max_valor > 1.70:
            mensaje = 'Existe la probabilidad que se produzcan mareas fuera de lo normal para la zona.'
        else:
            mensaje = 'Condición Normal'
        alertas.append({'fecha': str(fecha), 'alerta': mensaje, 'max_marea': round(max_valor,2)})
    alertas = sorted(alertas, key=lambda x: x['fecha'], reverse=True)
    return jsonify(alertas)

def generar_reporte_ultimas_alertas():
    df = cargar_pronostico_marea()
    if df is None:
        return None
    df['fecha_dia'] = df['fecha'].dt.date
    alertas = []
    for fecha, grupo in df.groupby('fecha_dia'):
        max_valor = grupo['keller_pronostico'].max()
        if max_valor > 1.70:
            mensaje = 'Existe la probabilidad que se produzcan mareas fuera de lo normal para la zona.'
        else:
            mensaje = 'Condición Normal'
        alertas.append({'fecha': str(fecha), 'alerta': mensaje, 'max_marea': round(max_valor,2)})
    alertas = sorted(alertas, key=lambda x: x['fecha'], reverse=True)[:4]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = f'reportes/reporte_ultimas_alertas_{timestamp}.txt'
    os.makedirs('reportes', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('REPORTE DE ÚLTIMAS 4 ALERTAS DE MAREAS\n')
        f.write('='*50 + '\n')
        for a in alertas:
            f.write(f"Fecha: {a['fecha']}\nAlerta: {a['alerta']}\nMáxima marea: {a['max_marea']} m\n{'-'*30}\n")
    return path

@app.route('/admin/generar_reporte_alertas')
def generar_reporte_alertas_endpoint():
    path = generar_reporte_ultimas_alertas()
    if path:
        return send_file(path, as_attachment=True)
    else:
        return 'No se pudo generar el reporte de alertas', 500

@app.route('/admin/descargar_alertas_historial')
def descargar_alertas_historial():
    df = cargar_pronostico_marea()
    if df is None:
        return 'No se pudo generar el historial', 500
    df['fecha_dia'] = df['fecha'].dt.date
    alertas = []
    for fecha, grupo in df.groupby('fecha_dia'):
        max_valor = grupo['keller_pronostico'].max()
        if max_valor > 1.70:
            mensaje = 'Existe la probabilidad que se produzcan mareas fuera de lo normal para la zona.'
        else:
            mensaje = 'Condición Normal'
        alertas.append({'fecha': str(fecha), 'alerta': mensaje, 'max_marea': round(max_valor,2)})
    alertas = sorted(alertas, key=lambda x: x['fecha'], reverse=True)
    path = 'reportes/historial_alertas.txt'
    with open(path, 'w', encoding='utf-8') as f:
        f.write('HISTORIAL COMPLETO DE ALERTAS DE MAREAS\n')
        f.write('='*50 + '\n')
        for a in alertas:
            f.write(f"Fecha: {a['fecha']}\nAlerta: {a['alerta']}\nMáxima marea: {a['max_marea']} m\n{'-'*30}\n")
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True) 