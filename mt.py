import tkinter as tk
from tkinter import filedialog, messagebox
from difflib import SequenceMatcher
import re
from tkinter import ttk
import tkinter.font as tkfont

class MaquinaDeTuring:
    def __init__(self, texto_original, texto_analizar):
        self.texto_original = texto_original.lower().strip()
        self.texto_analizar = texto_analizar.lower().strip()
        self.estado = 'q0'
        self.transiciones = []
        
    def calcular_similitud(self, str1, str2):
        # Dividir los textos en palabras
        palabras_str1 = str1.lower().split()
        palabras_str2 = str2.lower().split()
        
        # Buscar secuencias exactas de palabras
        max_coincidencia = 0
        palabras_consecutivas_minimas = 5
        
        # Crear ventanas de palabras del texto original
        ventanas_originales = set()
        for i in range(len(palabras_str1) - palabras_consecutivas_minimas + 1):
            ventana = tuple(palabras_str1[i:i + palabras_consecutivas_minimas])
            ventanas_originales.add(ventana)
        
        # Buscar coincidencias exactas en el texto a analizar
        encontro_coincidencia = False
        secuencias_encontradas = []
        
        # Primero verificar si hay cita textual
        match = re.search(r'[\'"](.+?)[\'"]', str2)
        if match:
            texto_entre_comillas = match.group(1).lower()
            # Verificar si el texto entre comillas coincide sustancialmente con el original
            for i in range(len(palabras_str1) - palabras_consecutivas_minimas + 1):
                segmento_original = ' '.join(palabras_str1[i:i + palabras_consecutivas_minimas])
                if segmento_original in texto_entre_comillas:
                    encontro_coincidencia = True
                    secuencias_encontradas.append(segmento_original)
                    similitud = len(texto_entre_comillas.split()) / len(palabras_str1)
                    return similitud, secuencias_encontradas
        
        # Si no hay citas, buscar coincidencias en el texto completo
        for i in range(len(palabras_str2) - palabras_consecutivas_minimas + 1):
            ventana = tuple(palabras_str2[i:i + palabras_consecutivas_minimas])
            if ventana in ventanas_originales:
                encontro_coincidencia = True
                secuencia = ' '.join(ventana)
                secuencias_encontradas.append(secuencia)
        
        if not encontro_coincidencia:
            return 0.0, []
        
        # Calcular similitud basada en las secuencias encontradas
        texto_coincidente = ' '.join(secuencias_encontradas)
        similitud = len(texto_coincidente.split()) / len(palabras_str1)
        
        return similitud, secuencias_encontradas
    
    def tiene_cita_apa(self):
        # Mejorar la detección de citas
        patrones_cita = [
            r'(?:según|como señala|como indica|como menciona|de acuerdo con)\s+[A-ZÀ-ÿ][a-zà-ÿ]+\s*\(\d{4}\)\s*,\s*[\'"].*?[\'"]',
            r'[\'"].*?[\'"]\s*\([A-ZÀ-ÿ][a-zà-ÿ]+,\s*\d{4}\)',
        ]
        
        for patron in patrones_cita:
            if re.search(patron, self.texto_analizar, re.IGNORECASE):
                return True
        return False
    
    def procesar(self):
        while True:
            if self.estado == 'q0':
                # Calcular similitud
                similitud, secuencias = self.calcular_similitud(self.texto_original, self.texto_analizar)
                self.transiciones.append(f"Estado: {self.estado} - Calculando similitud: {similitud*100:.2f}%")
                
                if secuencias:
                    self.transiciones.append("Secuencias encontradas:")
                    for seq in secuencias:
                        self.transiciones.append(f"- {seq}")
                
                if similitud >= 0.2:  # 20% del texto original
                    self.estado = 'q1'
                else:
                    self.estado = 'q3'
                    
            elif self.estado == 'q1':
                # Verificar si hay cita
                if self.tiene_cita_apa():
                    self.transiciones.append(f"Estado: {self.estado} - Cita encontrada")
                    self.estado = 'q2'
                else:
                    self.transiciones.append(f"Estado: {self.estado} - No se encontró cita")
                    self.estado = 'q4'
            
            elif self.estado == 'q2':
                self.resultado = "Texto correctamente citado"
                break
                
            elif self.estado == 'q3':
                self.resultado = "No hay coincidencias significativas"
                break
                
            elif self.estado == 'q4':
                self.resultado = "PLAGIO DETECTADO - Falta cita"
                break
        
        return self.resultado

def cargar_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
    if archivo:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                texto_original = f.read()
            entrada_archivo.delete(1.0, tk.END)
            entrada_archivo.insert(tk.END, texto_original)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el archivo: {str(e)}")

def verificar_plagio():
    texto_original = entrada_archivo.get("1.0", tk.END).strip()
    texto_analizar = entrada_texto.get("1.0", tk.END).strip()
    
    if not texto_original or not texto_analizar:
        messagebox.showwarning("Advertencia", "Por favor, ingrese ambos textos")
        return
    
    mt = MaquinaDeTuring(texto_original, texto_analizar)
    resultado = mt.procesar()
    
    # Configurar color según el resultado
    if "PLAGIO DETECTADO" in resultado:
        resultado_lbl.configure(fg='#e74c3c')  # Rojo para plagio
    elif "correctamente citado" in resultado:
        resultado_lbl.configure(fg='#27ae60')  # Verde para texto correcto
    else:
        resultado_lbl.configure(fg='#f39c12')  # Naranja para otros casos
    
    resultado_lbl.config(text=f"Resultado: {resultado}")
    
    transiciones_text.delete(1.0, tk.END)
    for transicion in mt.transiciones:
        transiciones_text.insert(tk.END, transicion + "\n")

# Interfaz gráfica
ventana = tk.Tk()
ventana.title("Detector de Plagio")
ventana.geometry("900x900")
ventana.configure(bg='#f0f0f0')  # Color de fondo suave

# Estilo para los widgets
style = ttk.Style()
style.configure('TButton', 
    padding=10, 
    font=('Arial', 10, 'bold'),
    background='#4a90e2'
)
style.configure('TLabel', 
    font=('Arial', 11),
    background='#f0f0f0'
)

# Frame principal
main_frame = ttk.Frame(ventana, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

# Título con estilo
titulo = tk.Label(main_frame, 
    text="Detector de Plagio con Máquina de Turing",
    font=("Arial", 18, "bold"),
    bg='#f0f0f0',
    fg='#2c3e50'
)
titulo.pack(pady=20)

# Frame para el texto original
frame_original = ttk.LabelFrame(main_frame, text="Texto Original", padding="10")
frame_original.pack(fill=tk.X, padx=10, pady=5)

boton_cargar = ttk.Button(frame_original, 
    text="Cargar archivo",
    command=cargar_archivo,
    style='TButton'
)
boton_cargar.pack(pady=5)

entrada_archivo = tk.Text(frame_original, 
    height=10, 
    width=70,
    font=('Arial', 10),
    wrap=tk.WORD,
    bg='white',
    relief=tk.SOLID,
    borderwidth=1
)
entrada_archivo.pack(pady=5)

# Frame para el texto a analizar
frame_analizar = ttk.LabelFrame(main_frame, text="Texto a Analizar", padding="10")
frame_analizar.pack(fill=tk.X, padx=10, pady=5)

entrada_texto = tk.Text(frame_analizar, 
    height=10, 
    width=70,
    font=('Arial', 10),
    wrap=tk.WORD,
    bg='white',
    relief=tk.SOLID,
    borderwidth=1
)
entrada_texto.pack(pady=5)

# Botón de verificación
boton_verificar = ttk.Button(main_frame, 
    text="Verificar Plagio",
    command=verificar_plagio,
    style='TButton'
)
boton_verificar.pack(pady=15)

# Resultado con estilo
resultado_lbl = tk.Label(main_frame, 
    text="",
    font=("Arial", 12, "bold"),
    bg='#f0f0f0',
    fg='#2c3e50'
)
resultado_lbl.pack(pady=10)

# Frame para transiciones
frame_transiciones = ttk.LabelFrame(main_frame, text="Proceso de Análisis", padding="10")
frame_transiciones.pack(fill=tk.X, padx=10, pady=5)

transiciones_text = tk.Text(frame_transiciones, 
    height=10, 
    width=70,
    font=('Arial', 10),
    wrap=tk.WORD,
    bg='white',
    relief=tk.SOLID,
    borderwidth=1
)
transiciones_text.pack(pady=5)

ventana.mainloop()
