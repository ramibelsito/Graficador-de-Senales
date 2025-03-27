# Graficador de señales CSV con GUI
# Autor: Ramiro Nahuel Belsito - Legajo: 62641 - rabelsito@itba.edu.ar

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, colorchooser, ttk
import matplotlib.font_manager as fm
import json # Para guardar y cargar configuraciones
import os

def permitir_scroll(root):
    # Contenedor principal con scrollbar
    contenedor = tk.Frame(root)
    contenedor.pack(fill="both", expand=True)

    canvas = tk.Canvas(contenedor)
    scrollbar = tk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
    frame_contenedor = tk.Frame(canvas)

    # Asociar el frame con el canvas
    def update_scroll_region(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(window_id, width=canvas.winfo_width())  # Ajustar ancho del frame

    frame_contenedor.bind("<Configure>", update_scroll_region)

    window_id = canvas.create_window((canvas.winfo_width() // 2, 0), window=frame_contenedor, anchor="n")

    canvas.configure(yscrollcommand=scrollbar.set)

    # Vincular el scroll con la rueda del mouse
    def on_mouse_wheel(event):
        canvas.yview_scroll(-1 * (event.delta // 120), "units")  # Windows
    
    def on_mouse_wheel_linux(event):
        if event.num == 4:
            canvas.yview_scroll(-1, "units")  # Scroll up
        elif event.num == 5:
            canvas.yview_scroll(1, "units")  # Scroll down

    canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # Windows
    canvas.bind_all("<Button-4>", on_mouse_wheel_linux)  # Linux (scroll up)
    canvas.bind_all("<Button-5>", on_mouse_wheel_linux)  # Linux (scroll down)

    # Redibujar cuando la ventana cambia de tamaño
    canvas.bind("<Configure>", update_scroll_region)

    # FORZAR la actualización tras iniciar la GUI
    root.after(100, update_scroll_region)

    # Posicionar los elementos
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return frame_contenedor



# Inicializar la ventana de la GUI
root = tk.Tk()
root.title("Graficador de Señales CSV")
root.geometry("500x600")
frame_contenedor = permitir_scroll(root)


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
def cargar_csv():
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
        
        actualizar_estado("Archivo cargado correctamente.")

# Función para cambiar la escala de tiempo
def cambiar_escala():
    global df, escala_tiempo
    escala_tiempo = escala_var.get()
    escalas = {"s": 1, "ms": 1e3, "us": 1e6, "ns": 1e9}
    if df is not None and escala_tiempo in escalas:
        df["Tiempo"] *= escalas[escala_tiempo]
        actualizar_estado(f"Escala de tiempo cambiada a {escala_tiempo}")

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
        actualizar_estado("Primero carga un archivo CSV.")


# Función para actualizar el estado
def actualizar_estado(texto):
    estado_label.config(text=texto)

# Manejo de Estilos

def actualizar_lista_estilos():
    if os.path.exists("estilos.json"):
        with open("estilos.json", "r") as f:
            estilos = json.load(f)
            estilos_menu["values"] = list(estilos.keys())  # Cargar nombres de estilos

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
        actualizar_estado("Ingresa un nombre para el estilo.")
        return
    
    # Cargar configuraciones previas
    estilos = {}
    if os.path.exists("estilos.json"):
        with open("estilos.json", "r") as f:
            estilos = json.load(f)

    # Guardar el nuevo estilo
    estilos[nombre_estilo] = config
    with open("estilos.json", "w") as f:
        json.dump(estilos, f, indent=4)
    
    # Actualizar lista de estilos disponibles
    actualizar_lista_estilos()
    actualizar_estado(f"Estilo '{nombre_estilo}' guardado.")
    # estilo entry vacio
    nombre_estilo_entry.delete(0, tk.END)

def cargar_estilo():
    global escala_tiempo, fuente_grafico, titulo_grafico, xlabel, ylabel, colores_canales, estilos_linea, nombres_canales
    
    estilo_seleccionado = estilos_var.get()
    if not estilo_seleccionado:
        actualizar_estado("Selecciona un estilo.")
        return
    
    if os.path.exists("estilos.json"):
        with open("estilos.json", "r") as f:
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
                
                actualizar_estado(f"Estilo '{estilo_seleccionado}' cargado.")

def borrar_estilo():
    estilo_seleccionado = estilos_var.get()
    if not estilo_seleccionado:
        actualizar_estado("Selecciona un estilo.")
        return
    
    if os.path.exists("estilos.json"):
        with open("estilos.json", "r") as f:
            estilos = json.load(f)
            if estilo_seleccionado in estilos:
                del estilos[estilo_seleccionado]
                with open("estilos.json", "w") as f:
                    json.dump(estilos, f, indent=4)
                
                # Actualizar lista de estilos disponibles
                actualizar_lista_estilos()
                actualizar_estado(f"Estilo '{estilo_seleccionado}' eliminado.")
                estilos_var.set(obtener_primer_estilo())
                estilos_menu.event_generate("<<ComboboxSelected>>")


# Elementos de la GUI
btn_cargar = tk.Button(frame_contenedor, text="Cargar CSV", command=cargar_csv)
btn_cargar.pack(pady=5)
escala_var = tk.StringVar(value=escala_tiempo)
escala_menu = ttk.Combobox(frame_contenedor, textvariable=escala_var, values=["s", "ms", "us", "ns"])
escala_menu.pack()
btn_cambiar_escala = tk.Button(frame_contenedor, text="Cambiar Escala", command=cambiar_escala)
btn_cambiar_escala.pack(pady=5)

#Entrada para fuente
# Selección de fuente
fuente_var = tk.StringVar(value=fuente_grafico)
fuente_menu = ttk.Combobox(frame_contenedor, textvariable=fuente_var, values=fuentes_disponibles)
fuente_menu.pack()
btn_fuente = tk.Button(frame_contenedor, text="Cambiar Fuente", command=cambiar_fuente)
btn_fuente.pack(pady=5)

# Entrada para título
titulo_entry = tk.Entry(frame_contenedor)
titulo_entry.pack()
btn_titulo = tk.Button(frame_contenedor, text="Cambiar Título", command=cambiar_titulo)
btn_titulo.pack(pady=5)

# Entradas para nombres de ejes
xlabel_entry = tk.Entry(frame_contenedor)
xlabel_entry.insert(0, "Tiempo")
xlabel_entry.pack()

ylabel_entry = tk.Entry(frame_contenedor)
ylabel_entry.insert(0, "Voltaje (V)")
ylabel_entry.pack()

btn_labels = tk.Button(frame_contenedor, text="Cambiar Nombres de Ejes", command=cambiar_labels)
btn_labels.pack(pady=5)

# Selección de canal para cambiar color
canal_color_var = tk.StringVar(value="0")
canal_color_menu = ttk.Combobox(frame_contenedor, textvariable=canal_color_var)
canal_color_menu.pack()
btn_color = tk.Button(frame_contenedor, text="Cambiar Color Canal", command=cambiar_color_canal)
btn_color.pack(pady=5)

# Selección de canal para cambiar estilo de línea
canal_estilo_var = tk.StringVar(value="0")
canal_estilo_menu = ttk.Combobox(frame_contenedor, textvariable=canal_estilo_var)
canal_estilo_menu.pack()

estilo_linea_var = tk.StringVar(value="-")
estilo_linea_menu = ttk.Combobox(frame_contenedor, textvariable=estilo_linea_var, values=["-", "--", ":", "-."])
estilo_linea_menu.pack()
btn_estilo = tk.Button(frame_contenedor, text="Cambiar Estilo Línea", command=cambiar_estilo_linea)
btn_estilo.pack(pady=5)

# Selección de canal para cambiar nombre
canal_nombre_var = tk.StringVar(value="0")
canal_nombre_menu = ttk.Combobox(frame_contenedor, textvariable=canal_nombre_var)
canal_nombre_menu.pack()

nombre_canal_entry = tk.Entry(frame_contenedor)
nombre_canal_entry.pack()
btn_nombre = tk.Button(frame_contenedor, text="Cambiar Nombre Canal", command=cambiar_nombre_canal)
btn_nombre.pack(pady=5)

# Entrada para el nombre del estilo
nombre_estilo_entry = tk.Entry(frame_contenedor)
nombre_estilo_entry.pack()
# Botón para guardar configuración
btn_guardar_configuracion = tk.Button(frame_contenedor, text="Guardar Estilo", command=guardar_configuracion)
btn_guardar_configuracion.pack(pady=5)
# Combobox para seleccionar estilos guardados
def obtener_primer_estilo():
    if os.path.exists("estilos.json"):
        with open("estilos.json", "r") as f:
            estilos = json.load(f)
            if estilos:
                return list(estilos.keys())[0]
    return ""
estilos_var = tk.StringVar(value=obtener_primer_estilo())
estilos_menu = ttk.Combobox(frame_contenedor, textvariable=estilos_var)
estilos_menu.pack()
# Botones para borrar y cargar configuración
frame_botones_estilos = tk.Frame(frame_contenedor)
frame_botones_estilos.pack(pady=5)
# Boton borrar
btn_borrar_estilo = tk.Button(frame_botones_estilos, text="Borrar Estilo", command=borrar_estilo)
btn_borrar_estilo.pack(side="left", padx=5)
# Boton cargar
btn_cargar_configuracion = tk.Button(frame_botones_estilos, text="Cargar Estilo", command=cargar_estilo)
btn_cargar_configuracion.pack(side="left", padx=5)
# Botón para graficar
btn_graficar = tk.Button(frame_contenedor, text="Graficar", command=graficar_senal)
btn_graficar.pack(pady=10)
btn_graficar.config(bg='green', fg='white')

estado_label = tk.Label(frame_contenedor, text="Seleccione un archivo CSV.")
estado_label.pack()

# Al inicio, actualizar la lista de estilos guardados
root.after(100, actualizar_lista_estilos)


root.mainloop()
