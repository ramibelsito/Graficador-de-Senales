# Graficador de señales CSV con GUI
# Autor: Ramiro Nahuel Belsito - Legajo: 62641 - rabelsito@itba.edu.ar

import os
try:
    import pandas as pd
except ImportError:
    os.system('pip install pandas')
    import pandas as pd
try:
    import numpy as np
except ImportError:
    os.system('pip install numpy')
    import numpy as np
try:
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
except ImportError:
    os.system('pip install matplotlib')
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
try:
    import tkinter as tk
    from tkinter import filedialog, colorchooser, ttk
except ImportError:
    os.system('pip install tk')
    import tkinter as tk
    from tkinter import filedialog, colorchooser, ttk
try:
    import json
except ImportError:
    os.system('pip install json')
    import json


# Inicializar la ventana de la GUI
root = tk.Tk()
root.title("Graficador de Señales CSV")
root.geometry("1920x1080")

# Crear el widget Notebook para las pestañas
notebook = ttk.Notebook(root)

# Crear los marcos que van a contener las pestañas
frame_graficador = ttk.Frame(notebook)
frame_bode = ttk.Frame(notebook)

# Agregar las pestañas al widget Notebook
notebook.add(frame_graficador, text="Graficador en Dominio Temporal")
notebook.add(frame_bode, text="Graficador de Bode")

# Empacar el widget Notebook en la ventana
notebook.pack(fill="both", expand=True)

# Variables globales
file_path = ""
colores_canales = []
escala_tiempo = "ms"  # Puede ser "s", "ms", "us", "ns"
df = None
titulo_grafico = "Señales del osciloscopio"
xlabel = "Tiempo"
ylabel = "Voltaje (V)"
estilos_linea = []
nombres_canales = []
fuente_grafico = "DejaVu Serif"  # Fuente por defecto


# Lista de fuentes disponibles
fuentes_disponibles = []
for f in fm.findSystemFonts(fontpaths=None, fontext='ttf'):
    try:
        font_name = fm.FontProperties(fname=f).get_name()
        fuentes_disponibles.append(font_name)
    except Exception as e:
        print(f"Error loading font {f}: {e}")

# Asegurarse de incluir fuentes comunes si están disponibles
fuentes_comunes = ["Times New Roman", "Arial", "Helvetica"]
for fuente in fuentes_comunes:
    if fuente not in fuentes_disponibles:
        fuentes_disponibles.append(fuente)

# Ordenar lista de fuentes en orden alfabético
fuentes_disponibles.sort()


# Función para cargar el archivo CSV
def cargar_csv_graficador():
    global df, file_path, colores_canales, estilos_linea, nombres_canales
    file_path = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")])
    if file_path:
        df = pd.read_csv(file_path)
        num_canales = len(df.columns) - 1
        
        df.columns = ["Tiempo"] + [f"Canal {i}" for i in range(1, num_canales + 1)]
        df = df.iloc[1:].reset_index(drop=True)
        df = df.apply(pd.to_numeric, errors="coerce")
        
        # Inicializar colores, estilos y nombres
        colores_canales = ["C" + str(i) for i in range(num_canales)]
        estilos_linea = ["-"] * num_canales
        nombres_canales = [f"Canal {i}" for i in range(1, num_canales + 1)]
        
        # Actualizar opciones en los Combobox
        opciones_canales = [str(i) for i in range(num_canales)]
        canal_color_menu["values"] = opciones_canales
        canal_color_var.set("0")
        canal_estilo_menu["values"] = opciones_canales
        canal_estilo_var.set("0")
        canal_nombre_menu["values"] = opciones_canales
        canal_nombre_var.set("0")
        
        actualizar_estado("Archivo cargado correctamente.", estado_label)

def cargar_csv_bode():
    global df, file_path
    file_path = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")])
    if not file_path:
        actualizar_estado("No se seleccionó ningún archivo.", estado_label_bode)
    else:
        global frecuencias, ganancias, fases, amplitudes, amplitud
        # Leer el archivo CSV
        df = pd.read_csv(file_path, skiprows=1, encoding='latin1')
        # Renombrar las columnas
        df.columns = ['Index', 'Frequency (Hz)', 'Amplitude (Vpp)', 'Gain (dB)', 'Phase (°)']
        # Eliminar la columna de índice
        df.drop(columns=['Index'], inplace=True)
        # Convertir las columnas a tipo numérico
        df['Frequency (Hz)'] = pd.to_numeric(df['Frequency (Hz)'], errors='coerce')
        df['Amplitude (Vpp)'] = pd.to_numeric(df['Amplitude (Vpp)'], errors='coerce')
        df['Gain (dB)'] = pd.to_numeric(df['Gain (dB)'], errors='coerce')
        df['Phase (°)'] = pd.to_numeric(df['Phase (°)'], errors='coerce')
        frecuencias = df['Frequency (Hz)'].tolist()
        ganancias = df['Gain (dB)'].tolist()
        fases = df['Phase (°)'].tolist()
        amplitudes = df['Amplitude (Vpp)'].tolist()
        amplitud = amplitudes[1]

        actualizar_estado("Archivo cargado correctamente.", estado_label_bode)
# Función para cambiar la escala de tiempo
def cambiar_escala():
    global df, escala_tiempo
    escala_tiempo = escala_var.get()
    escalas = {"s": 1, "ms": 1e3, "us": 1e6, "ns": 1e9}
    if df is not None and escala_tiempo in escalas:
        df["Tiempo"] *= escalas[escala_tiempo]
        actualizar_estado(f"Escala de tiempo cambiada a {escala_tiempo}", estado_label)

# Función para cambiar la fuente del gráfico
def cambiar_fuente():
    global fuente_grafico
    fuente_grafico = fuente_var.get()

# Función para cambiar el título
def cambiar_titulo():
    global titulo_grafico
    titulo_grafico = titulo_entry.get()

# Función para cambiar los nombres de los ejes
def cambiar_labels():
    global xlabel, ylabel
    xlabel = xlabel_entry.get()
    ylabel = ylabel_entry.get()

# Función para cambiar el color de un canal
def cambiar_color_canal():
    global colores_canales
    idx = int(canal_color_var.get())
    colores_canales[idx] = colorchooser.askcolor()[1]

# Función para cambiar el estilo de línea
def cambiar_estilo_linea():
    global estilos_linea
    idx = int(canal_estilo_var.get())
    estilos_linea[idx] = estilo_linea_var.get()

# Función para cambiar el nombre de un canal
def cambiar_nombre_canal():
    global nombres_canales
    idx = int(canal_nombre_var.get())
    nombres_canales[idx] = nombre_canal_entry.get()


# Función para graficar los datos
def graficar_senal():
    if df is not None:
        plt.figure(figsize=(10, 5))

        # Ajustar el tiempo para que inicie en 0
        tiempo_ajustado = df["Tiempo"] - df["Tiempo"].min()

        for i, canal in enumerate(df.columns[1:]):
            plt.plot(tiempo_ajustado, df[canal], label=nombres_canales[i], 
                     color=colores_canales[i], linestyle=estilos_linea[i])

        # Aplicar la fuente seleccionada
        font_properties = fm.FontProperties(fname=fm.findfont(fm.FontProperties(family=fuente_grafico)))

        # Etiquetas y título
        plt.xlabel(f"{xlabel} ({escala_tiempo})", fontproperties=font_properties)
        plt.ylabel(ylabel, fontproperties=font_properties)
        plt.title(titulo_grafico, fontproperties=font_properties)
        
        # Configuración de la leyenda y la cuadrícula
        plt.legend(prop={'family': font_properties.get_name()})
        plt.grid()

        plt.show()
    else:
        actualizar_estado("Primero carga un archivo CSV.", estado_label)


opciones ={"color": "r", "estilo_linea": "-", "titulo_mag": "", "titulo_fase": "", "grid": True, "titulo_general": "", "etiqueta_x": "Frecuencia [rad/s]", "etiqueta_y_mag": "Magnitud [dB]", "etiqueta_y_fase": "Fase [°]", "tamaño_fuente": 12, "alpha": 0.8, "color_fondo": "white"}
# Funciones para editar opciones desde la GUI

def cambiar_color_bode():
    opciones["color"] = colorchooser.askcolor()[1]
    actualizar_estado("Color cambiado.", estado_label_bode)

def cambiar_estilo_linea_bode():
    opciones["estilo_linea"] = estilo_linea_bode_var.get()
    actualizar_estado("Estilo de línea cambiado.", estado_label_bode)

def cambiar_titulo_mag_bode():
    opciones["titulo_mag"] = titulo_mag_bode_entry.get()
    actualizar_estado("Título de magnitud cambiado.", estado_label_bode)

def cambiar_titulo_fase_bode():
    opciones["titulo_fase"] = titulo_fase_bode_entry.get()
    actualizar_estado("Título de fase cambiado.", estado_label_bode)

def cambiar_titulo_general_bode():
    opciones["titulo_general"] = titulo_general_bode_entry.get()
    actualizar_estado("Título general cambiado.", estado_label_bode)

def cambiar_etiqueta_x_bode():
    opciones["etiqueta_x"] = etiqueta_x_bode_entry.get()
    actualizar_estado("Etiqueta X cambiada.", estado_label_bode)

def cambiar_etiqueta_y_mag_bode():
    opciones["etiqueta_y_mag"] = etiqueta_y_mag_bode_entry.get()
    actualizar_estado("Etiqueta Y de magnitud cambiada.", estado_label_bode)

def cambiar_etiqueta_y_fase_bode():
    opciones["etiqueta_y_fase"] = etiqueta_y_fase_bode_entry.get()
    actualizar_estado("Etiqueta Y de fase cambiada.", estado_label_bode)

def cambiar_tamaño_fuente_bode():
    opciones["tamaño_fuente"] = int(tamaño_fuente_bode_entry.get())
    actualizar_estado("Tamaño de fuente cambiado.", estado_label_bode)

def cambiar_alpha_bode():
    opciones["alpha"] = float(alpha_bode_entry.get())
    actualizar_estado("Transparencia (alpha) cambiada.", estado_label_bode)

def cambiar_color_fondo_bode():
    opciones["color_fondo"] = colorchooser.askcolor()[1]
    actualizar_estado("Color de fondo cambiado.", estado_label_bode)

def cambiar_fuente_bode():
    opciones["fuente"] = fuente_bode_var.get()
    actualizar_estado("Fuente cambiada.", estado_label_bode)

def graficar_bode():
    global frecuencias, ganancias, fases, amplitudes, amplitud, opciones
    opciones = opciones or {}
    color = opciones.get("color", "b")
    estilo_linea = opciones.get("estilo_linea", "-")
    titulo_mag = opciones.get("titulo_mag", "Diagrama de Bode - Magnitud")
    titulo_fase = opciones.get("titulo_fase", "Diagrama de Bode - Fase")
    etiqueta_x = opciones.get("etiqueta_x", "Frecuencia [rad/s]")
    etiqueta_y_mag = opciones.get("etiqueta_y_mag", "Magnitud [dB]")
    etiqueta_y_fase = opciones.get("etiqueta_y_fase", "Fase [°]")
    grid = opciones.get("grid", True)
    tamaño_fuente = opciones.get("tamaño_fuente", 12)
    alpha = opciones.get("alpha", 0.8)
    titulo_general = opciones.get("titulo_general", "Diagrama de Bode Personalizado")
    color_fondo = opciones.get("color_fondo", "white")
    
    # Ventana para el gráfico de Magnitud
    fig_mag = plt.figure(figsize=(8, 6))
    fig_mag.suptitle(titulo_general, fontsize=tamaño_fuente + 2)
    fig_mag.patch.set_facecolor(color_fondo)
    ax_mag = fig_mag.add_subplot(111)
    ax_mag.semilogx(frecuencias, ganancias, color=color, linestyle=estilo_linea, alpha=alpha)
    ax_mag.set_title(titulo_mag, fontsize=tamaño_fuente)
    ax_mag.set_xlabel(etiqueta_x, fontsize=tamaño_fuente)
    ax_mag.set_ylabel(etiqueta_y_mag, fontsize=tamaño_fuente)
    ax_mag.grid(grid)
    ax_mag.set_facecolor(color_fondo)
    
    # Ventana para el gráfico de Fase
    fig_fase = plt.figure(figsize=(8, 6))
    fig_fase.suptitle(titulo_general, fontsize=tamaño_fuente + 2)
    fig_fase.patch.set_facecolor(color_fondo)
    ax_fase = fig_fase.add_subplot(111)
    ax_fase.semilogx(frecuencias, fases, color=color, linestyle=estilo_linea, alpha=alpha)
    ax_fase.set_title(titulo_fase, fontsize=tamaño_fuente)
    ax_fase.set_xlabel(etiqueta_x, fontsize=tamaño_fuente)
    ax_fase.set_ylabel(etiqueta_y_fase, fontsize=tamaño_fuente)
    ax_fase.grid(grid)
    ax_fase.set_facecolor(color_fondo)
    
    # Mostrar ambas ventanas
    plt.show()

# Función para actualizar el estado

def actualizar_estado(texto, estado_label):
    estado_label.config(text=texto)

# Manejo de Estilos

def actualizar_lista_estilos():
    if os.path.exists("./Graficador-de-Senales/estilos.json"):
        with open("./Graficador-de-Senales/estilos.json", "r") as f:
            estilos = json.load(f)
            estilos_menu["values"] = list(estilos.keys())  # Cargar nombres de estilos
    else:
        print("No se encontró el archivo de estilos.")

def guardar_configuracion():
    config = {
        "escala_tiempo": escala_tiempo,
        "fuente_grafico": fuente_grafico,
        "titulo_grafico": titulo_grafico,
        "xlabel": xlabel,
        "ylabel": ylabel,
        "colores_canales": colores_canales,
        "estilos_linea": estilos_linea,
        "nombres_canales": nombres_canales
    }
    
    nombre_estilo = nombre_estilo_entry.get().strip()
    if not nombre_estilo:
        actualizar_estado("Ingresa un nombre para el estilo.", estado_label)
        return
    
    # Cargar configuraciones previas
    estilos = {}
    if os.path.exists("./Graficador-de-Senales/estilos.json"):
        with open("./Graficador-de-Senales/estilos.json", "r") as f:
            estilos = json.load(f)
    else:
        with open("./Graficador-de-Senales/estilos.json", "w") as f:
            json.dump({}, f, indent=4)


    # Guardar el nuevo estilo
    estilos[nombre_estilo] = config
    with open("./Graficador-de-Senales/estilos.json", "w") as f:
        json.dump(estilos, f, indent=4)
    
    # Actualizar lista de estilos disponibles
    actualizar_lista_estilos()
    actualizar_estado(f"Estilo '{nombre_estilo}' guardado.", estado_label)
    # estilo entry vacio
    nombre_estilo_entry.delete(0, tk.END)

def cargar_estilo():
    global escala_tiempo, fuente_grafico, titulo_grafico, xlabel, ylabel, colores_canales, estilos_linea, nombres_canales
    
    estilo_seleccionado = estilos_var.get()
    if not estilo_seleccionado:
        actualizar_estado("Selecciona un estilo.", estado_label)
        return
    
    if os.path.exists("./Graficador-de-Senales/estilos.json"):
        with open("./Graficador-de-Senales/estilos.json", "r") as f:
            estilos = json.load(f)
            if estilo_seleccionado in estilos:
                config = estilos[estilo_seleccionado]
                escala_tiempo = config["escala_tiempo"]
                fuente_grafico = config["fuente_grafico"]
                titulo_grafico = config["titulo_grafico"]
                xlabel = config["xlabel"]
                ylabel = config["ylabel"]
                colores_canales = config["colores_canales"]
                estilos_linea = config["estilos_linea"]
                nombres_canales = config["nombres_canales"]
                
                actualizar_estado(f"Estilo '{estilo_seleccionado}' cargado.", estado_label)

def borrar_estilo():
    estilo_seleccionado = estilos_var.get()
    if not estilo_seleccionado:
        actualizar_estado("Selecciona un estilo.", estado_label)
        return
    
    if os.path.exists("./Graficador-de-Senales/estilos.json"):
        with open("./Graficador-de-Senales/estilos.json", "r") as f:
            estilos = json.load(f)
            if estilo_seleccionado in estilos:
                del estilos[estilo_seleccionado]
                with open("./Graficador-de-Senales/estilos.json", "w") as f:
                    json.dump(estilos, f, indent=4)
                
                # Actualizar lista de estilos disponibles
                actualizar_lista_estilos()
                actualizar_estado(f"Estilo '{estilo_seleccionado}' eliminado.", estado_label)
                estilos_var.set(obtener_primer_estilo())
                estilos_menu.event_generate("<<ComboboxSelected>>")

def obtener_primer_estilo():
        if os.path.exists("./Graficador-de-Senales/estilos.json"):
            with open("./Graficador-de-Senales/estilos.json", "r") as f:
                estilos = json.load(f)
                if estilos:
                    return list(estilos.keys())[0]
        return ""
# GUI 

def inicializar_gui_graficador():
    global escala_var, fuente_var, titulo_entry, xlabel_entry, ylabel_entry
    global canal_color_var, canal_color_menu, canal_estilo_var, canal_estilo_menu
    global estilo_linea_var, estilo_linea_menu, canal_nombre_var, canal_nombre_menu
    global nombre_canal_entry, nombre_estilo_entry, estilos_var, estilos_menu, estado_label

    # Elementos de la GUI
    btn_cargar = tk.Button(frame_graficador, text="Cargar CSV", command=cargar_csv_graficador)
    btn_cargar.pack(pady=5)
    escala_var = tk.StringVar(value=escala_tiempo)
    escala_menu = ttk.Combobox(frame_graficador, textvariable=escala_var, values=["s", "ms", "us", "ns"])
    escala_menu.pack()
    btn_cambiar_escala = tk.Button(frame_graficador, text="Cambiar Escala", command=cambiar_escala)
    btn_cambiar_escala.pack(pady=5)

    # Selección de fuente
    fuente_var = tk.StringVar(value=fuente_grafico)
    fuente_menu = ttk.Combobox(frame_graficador, textvariable=fuente_var, values=fuentes_disponibles)
    fuente_menu.pack()
    btn_fuente = tk.Button(frame_graficador, text="Cambiar Fuente", command=cambiar_fuente)
    btn_fuente.pack(pady=5)

    # Entrada para título
    titulo_entry = tk.Entry(frame_graficador)
    titulo_entry.pack()
    btn_titulo = tk.Button(frame_graficador, text="Cambiar Título", command=cambiar_titulo)
    btn_titulo.pack(pady=5)

    # Entradas para nombres de ejes
    xlabel_entry = tk.Entry(frame_graficador)
    xlabel_entry.insert(0, "Tiempo")
    xlabel_entry.pack()
    ylabel_entry = tk.Entry(frame_graficador)
    ylabel_entry.insert(0, "Voltaje (V)")
    ylabel_entry.pack()

    btn_labels = tk.Button(frame_graficador, text="Cambiar Nombres de Ejes", command=cambiar_labels)
    btn_labels.pack(pady=5)

    # Selección de canal para cambiar color
    canal_color_var = tk.StringVar(value="0")
    canal_color_menu = ttk.Combobox(frame_graficador, textvariable=canal_color_var)
    canal_color_menu.pack()
    btn_color = tk.Button(frame_graficador, text="Cambiar Color Canal", command=cambiar_color_canal)
    btn_color.pack(pady=5)

    # Selección de canal para cambiar estilo de línea
    canal_estilo_var = tk.StringVar(value="0")
    canal_estilo_menu = ttk.Combobox(frame_graficador, textvariable=canal_estilo_var)
    canal_estilo_menu.pack()

    estilo_linea_var = tk.StringVar(value="-")
    estilo_linea_menu = ttk.Combobox(frame_graficador, textvariable=estilo_linea_var, values=["-", "--", ":", "-."])
    estilo_linea_menu.pack()
    btn_estilo = tk.Button(frame_graficador, text="Cambiar Estilo Línea", command=cambiar_estilo_linea)
    btn_estilo.pack(pady=5)

    # Selección de canal para cambiar nombre
    canal_nombre_var = tk.StringVar(value="0")
    canal_nombre_menu = ttk.Combobox(frame_graficador, textvariable=canal_nombre_var)
    canal_nombre_menu.pack()

    nombre_canal_entry = tk.Entry(frame_graficador)
    nombre_canal_entry.pack()
    btn_nombre = tk.Button(frame_graficador, text="Cambiar Nombre Canal", command=cambiar_nombre_canal)
    btn_nombre.pack(pady=5)

    # Entrada para el nombre del estilo
    nombre_estilo_entry = tk.Entry(frame_graficador)
    nombre_estilo_entry.pack()
    # Botón para guardar configuración
    btn_guardar_configuracion = tk.Button(frame_graficador, text="Guardar Estilo", command=guardar_configuracion)
    btn_guardar_configuracion.pack(pady=5)
    # Combobox para seleccionar estilos guardados
    
    estilos_var = tk.StringVar(value=obtener_primer_estilo())
    estilos_menu = ttk.Combobox(frame_graficador, textvariable=estilos_var)
    estilos_menu.pack()
    # Botones para borrar y cargar configuración
    frame_botones_estilos = tk.Frame(frame_graficador)
    frame_botones_estilos.pack(pady=5)
    # Boton borrar
    btn_borrar_estilo = tk.Button(frame_botones_estilos, text="Borrar Estilo", command=borrar_estilo)
    btn_borrar_estilo.pack(side="left", padx=5)
    # Boton cargar
    btn_cargar_configuracion = tk.Button(frame_botones_estilos, text="Cargar Estilo", command=cargar_estilo)
    btn_cargar_configuracion.pack(side="left", padx=5)
    # Botón para graficar
    btn_graficar = tk.Button(frame_graficador, text="Graficar", command=graficar_senal)
    btn_graficar.pack(pady=10)
    btn_graficar.config(bg='green', fg='white')

    estado_label = tk.Label(frame_graficador, text="Seleccione un archivo CSV.")
    estado_label.pack()
def guardar_configuracion_bode():
    config = {
        "color": opciones["color"],
        "estilo_linea": opciones["estilo_linea"],
        "titulo_mag": opciones["titulo_mag"],
        "titulo_fase": opciones["titulo_fase"],
        "titulo_general": opciones["titulo_general"],
        "etiqueta_x": opciones["etiqueta_x"],
        "etiqueta_y_mag": opciones["etiqueta_y_mag"],
        "etiqueta_y_fase": opciones["etiqueta_y_fase"],
        "tamaño_fuente": opciones["tamaño_fuente"],
        "alpha": opciones["alpha"],
        "color_fondo": opciones["color_fondo"],
        "fuente": opciones.get("fuente", "DejaVu Serif")
    }

    nombre_estilo = nombre_estilo_bode_entry.get().strip()
    if not nombre_estilo:
        actualizar_estado("Ingresa un nombre para el estilo.", estado_label_bode)
        return

    # Cargar configuraciones previas
    estilos = {}
    if os.path.exists("./Graficador-de-Senales/estilos_bode.json"):
        with open("./Graficador-de-Senales/estilos_bode.json", "r") as f:
            estilos = json.load(f)
    else:
        with open("./Graficador-de-Senales/estilos_bode.json", "w") as f:
            json.dump({}, f, indent=4)

    # Guardar el nuevo estilo
    estilos[nombre_estilo] = config
    with open("./Graficador-de-Senales/estilos_bode.json", "w") as f:
        json.dump(estilos, f, indent=4)

    # Actualizar lista de estilos disponibles
    actualizar_lista_estilos_bode()
    actualizar_estado(f"Estilo '{nombre_estilo}' guardado.", estado_label_bode)
    nombre_estilo_bode_entry.delete(0, tk.END)

def cargar_estilo_bode():
    estilo_seleccionado = estilos_bode_var.get()
    if not estilo_seleccionado:
        actualizar_estado("Selecciona un estilo.", estado_label_bode)
        return

    if os.path.exists("./Graficador-de-Senales/estilos_bode.json"):
        with open("./Graficador-de-Senales/estilos_bode.json", "r") as f:
            estilos = json.load(f)
            if estilo_seleccionado in estilos:
                config = estilos[estilo_seleccionado]
                opciones.update(config)
                actualizar_estado(f"Estilo '{estilo_seleccionado}' cargado.", estado_label_bode)

def borrar_estilo_bode():
    estilo_seleccionado = estilos_bode_var.get()
    if not estilo_seleccionado:
        actualizar_estado("Selecciona un estilo.", estado_label_bode)
        return

    if os.path.exists("./Graficador-de-Senales/estilos_bode.json"):
        with open("./Graficador-de-Senales/estilos_bode.json", "r") as f:
            estilos = json.load(f)
            if estilo_seleccionado in estilos:
                del estilos[estilo_seleccionado]
                with open("./Graficador-de-Senales/estilos_bode.json", "w") as f:
                    json.dump(estilos, f, indent=4)

                # Actualizar lista de estilos disponibles
                actualizar_lista_estilos_bode()
                actualizar_estado(f"Estilo '{estilo_seleccionado}' eliminado.", estado_label_bode)
                estilos_bode_var.set(obtener_primer_estilo_bode())
                estilos_bode_menu.event_generate("<<ComboboxSelected>>")

def actualizar_lista_estilos_bode():
    if os.path.exists("./Graficador-de-Senales/estilos_bode.json"):
        with open("./Graficador-de-Senales/estilos_bode.json", "r") as f:
            estilos = json.load(f)
            estilos_bode_menu["values"] = list(estilos.keys())  # Cargar nombres de estilos
    else:
        print("No se encontró el archivo de estilos.")

def obtener_primer_estilo_bode():
    if os.path.exists("./Graficador-de-Senales/estilos_bode.json"):
        with open("./Graficador-de-Senales/estilos_bode.json", "r") as f:
            estilos = json.load(f)
            if estilos:
                return list(estilos.keys())[0]
    return ""

    
def inicializar_gui_bode():
    global estilo_linea_bode_var, titulo_mag_bode_entry, titulo_fase_bode_entry
    global titulo_general_bode_entry, etiqueta_x_bode_entry, etiqueta_y_mag_bode_entry
    global etiqueta_y_fase_bode_entry, tamaño_fuente_bode_entry, alpha_bode_entry
    global fuente_bode_var, fuente_bode_menu, nombre_estilo_bode_entry, estilos_bode_var, estilos_bode_menu

    global estado_label_bode
    # Agregar boton cargar archivo
    btn_cargar = tk.Button(frame_bode, text="Cargar CSV", command=cargar_csv_bode)
    btn_cargar.pack(pady=5)

    # Cambiar color
    btn_color_bode = tk.Button(frame_bode, text="Cambiar Color", command=cambiar_color_bode)
    btn_color_bode.pack(pady=5)

    # Cambiar estilo de línea
    estilo_linea_bode_var = tk.StringVar(value=opciones["estilo_linea"])
    estilo_linea_bode_menu = ttk.Combobox(frame_bode, textvariable=estilo_linea_bode_var, values=["-", "--", ":", "-."])
    estilo_linea_bode_menu.pack()
    btn_estilo_linea_bode = tk.Button(frame_bode, text="Cambiar Estilo Línea", command=cambiar_estilo_linea_bode)
    btn_estilo_linea_bode.pack(pady=5)

    # Cambiar títulos
    titulo_mag_bode_entry = tk.Entry(frame_bode)
    titulo_mag_bode_entry.insert(0, opciones["titulo_mag"])
    titulo_mag_bode_entry.pack()
    btn_titulo_mag_bode = tk.Button(frame_bode, text="Cambiar Título Magnitud", command=cambiar_titulo_mag_bode)
    btn_titulo_mag_bode.pack(pady=5)

    titulo_fase_bode_entry = tk.Entry(frame_bode)
    titulo_fase_bode_entry.insert(0, opciones["titulo_fase"])
    titulo_fase_bode_entry.pack()
    btn_titulo_fase_bode = tk.Button(frame_bode, text="Cambiar Título Fase", command=cambiar_titulo_fase_bode)
    btn_titulo_fase_bode.pack(pady=5)

    titulo_general_bode_entry = tk.Entry(frame_bode)
    titulo_general_bode_entry.insert(0, opciones["titulo_general"])
    titulo_general_bode_entry.pack()
    btn_titulo_general_bode = tk.Button(frame_bode, text="Cambiar Título General", command=cambiar_titulo_general_bode)
    btn_titulo_general_bode.pack(pady=5)

    # Cambiar etiquetas
    etiqueta_x_bode_entry = tk.Entry(frame_bode)
    etiqueta_x_bode_entry.insert(0, opciones["etiqueta_x"])
    etiqueta_x_bode_entry.pack()
    btn_etiqueta_x_bode = tk.Button(frame_bode, text="Cambiar Etiqueta X", command=cambiar_etiqueta_x_bode)
    btn_etiqueta_x_bode.pack(pady=5)

    etiqueta_y_mag_bode_entry = tk.Entry(frame_bode)
    etiqueta_y_mag_bode_entry.insert(0, opciones["etiqueta_y_mag"])
    etiqueta_y_mag_bode_entry.pack()
    btn_etiqueta_y_mag_bode = tk.Button(frame_bode, text="Cambiar Etiqueta Y Magnitud", command=cambiar_etiqueta_y_mag_bode)
    btn_etiqueta_y_mag_bode.pack(pady=5)

    etiqueta_y_fase_bode_entry = tk.Entry(frame_bode)
    etiqueta_y_fase_bode_entry.insert(0, opciones["etiqueta_y_fase"])
    etiqueta_y_fase_bode_entry.pack()
    btn_etiqueta_y_fase_bode = tk.Button(frame_bode, text="Cambiar Etiqueta Y Fase", command=cambiar_etiqueta_y_fase_bode)
    btn_etiqueta_y_fase_bode.pack(pady=5)

    # Cambiar tamaño de fuente
    tamaño_fuente_bode_entry = tk.Entry(frame_bode)
    tamaño_fuente_bode_entry.insert(0, str(opciones["tamaño_fuente"]))
    tamaño_fuente_bode_entry.pack()
    btn_tamaño_fuente_bode = tk.Button(frame_bode, text="Cambiar Tamaño Fuente", command=cambiar_tamaño_fuente_bode)
    btn_tamaño_fuente_bode.pack(pady=5)

    # Cambiar alpha
    alpha_bode_entry = tk.Entry(frame_bode)
    alpha_bode_entry.insert(0, str(opciones["alpha"]))
    alpha_bode_entry.pack()
    btn_alpha_bode = tk.Button(frame_bode, text="Cambiar Alpha", command=cambiar_alpha_bode)
    btn_alpha_bode.pack(pady=5)

    # Cambiar color de fondo
    btn_color_fondo_bode = tk.Button(frame_bode, text="Cambiar Color Fondo", command=cambiar_color_fondo_bode)
    btn_color_fondo_bode.pack(pady=5)

    # Cambiar fuente
    fuente_bode_var = tk.StringVar(value=opciones.get("fuente", "DejaVu Serif"))
    fuente_bode_menu = ttk.Combobox(frame_bode, textvariable=fuente_bode_var, values=fuentes_disponibles)
    fuente_bode_menu.pack()
    btn_fuente_bode = tk.Button(frame_bode, text="Cambiar Fuente", command=cambiar_fuente_bode)
    btn_fuente_bode.pack(pady=5)
    # GUI para estilos de Bode
    nombre_estilo_bode_entry = tk.Entry(frame_bode)
    nombre_estilo_bode_entry.pack()
    nombre_estilo_bode_entry = tk.Entry(frame_bode)
    nombre_estilo_bode_entry.pack()
    btn_guardar_configuracion_bode = tk.Button(frame_bode, text="Guardar Estilo", command=guardar_configuracion_bode)
    btn_guardar_configuracion_bode.pack(pady=5)

    estilos_bode_var = tk.StringVar(value=obtener_primer_estilo_bode())
    estilos_bode_menu = ttk.Combobox(frame_bode, textvariable=estilos_bode_var)
    estilos_bode_menu.pack()

    frame_botones_estilos_bode = tk.Frame(frame_bode)
    frame_botones_estilos_bode.pack(pady=5)
    btn_borrar_estilo_bode = tk.Button(frame_botones_estilos_bode, text="Borrar Estilo", command=borrar_estilo_bode)
    btn_borrar_estilo_bode.pack(side="left", padx=5)
    btn_cargar_configuracion_bode = tk.Button(frame_botones_estilos_bode, text="Cargar Estilo", command=cargar_estilo_bode)
    btn_cargar_configuracion_bode.pack(side="left", padx=5)
    # Agregar boton graficar
    btn_graficar = tk.Button(frame_bode, text="Graficar Bode", command=graficar_bode)
    btn_graficar.pack(pady=10)
    btn_graficar.config(bg='green', fg='white')
    # Agregar label de estado
    estado_label_bode = tk.Label(frame_bode)
    estado_label_bode.pack()
    estado_label_bode.config(text="Seleccione un archivo CSV.")

# Llamar a la función para inicializar la GUI del graficador
inicializar_gui_graficador()
inicializar_gui_bode()

# Al inicio, actualizar la lista de estilos guardados
root.after(100, lambda: [actualizar_lista_estilos(), actualizar_lista_estilos_bode()])


root.mainloop()
