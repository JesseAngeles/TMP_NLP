import os
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
from pymongo import MongoClient
from openai import OpenAI
from datetime import datetime

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuración del cliente de OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configuración de MongoDB
mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["instrucciones_db"]
collection = db["instrucciones"]

def generate_code(keywords):
    """Genera código en C++ en función de un prompt dado."""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un generador de código C++."},
                {"role": "user", "content": f"Genera código en C++ que haga lo siguiente {keywords}"
                 "Respuesta en formato codigo cpp (```cpp)"
                 "No escribas comentarios. "
                 "Escribe unicamente el codigo."
                 "Escribe unicamente la función solicitada."
                 "Los nombres de las funciones deben ser con el siguiente formato: FunctionN donde N es el numero."
                 "No escribas cout si no lo pide el prompt."
                 "Solo puedes utilizar la libreria de iostream"
                 "No escribas std"}
            ],
            temperature=0
        )
        code = response.choices[0].message.content.strip()
        print(code)
        if code.startswith("```") and code.endswith("```"):
            code = code[6:-3].strip()  # Elimina las comillas de código
        else:
            code = "No fue posible generar la petición"
        return code
    except Exception as e:
        print(f"Error al generar el código: {e}")
        return None

def extract_keywords(prompt):
    """Extrae las palabras principales de un prompt dado"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Identifcas instrucciones en formato (verbo en inifinito + complemento)"},
                {"role": "user", "content": f"Identifica todas las instrucciones por separado del siguiente prompt: {prompt}"}
            ],
            temperature=1
        )
        code = response.choices[0].message.content.strip()
        return code
    except Exception as e:
        print(f"Error al generar el codigo: {e}")
        return None


class CodeGenerator:
    def __init__(self):
        # Configuración inicial de la ventana principal
        self.root = tk.Tk()
        self.root.title("Generador de Código C++")
        self.root.geometry("500x450")

        # Elementos de la interfaz
        tk.Label(self.root, text="Escribe tu descripción:").pack(pady=10)

        # Campo de entrada de texto
        self.entry = tk.Text(self.root, height=5, width=50)
        self.entry.pack()

        # Botón para generar el código
        self.generate_button = tk.Button(self.root, text="Generar Código", command=self.generate_and_display_code)
        self.generate_button.pack(pady=10)

        # Botón para guardar el código en un archivo
        self.save_button = tk.Button(self.root, text="Guardar en code.cpp", command=self.save_code_to_file)
        self.save_button.pack_forget()

        # Área de salida para mostrar el código generado
        self.output = tk.Text(self.root, height=10, width=50, state="disabled")
        self.output.pack()

        # Variable para almacenar el código generado
        self.generated_code = ""

    def generate_and_display_code(self):
        """Toma el prompt, genera el código en C++ y lo muestra en el área de salida."""
        prompt = self.entry.get("1.0", "end-1c")  # Obtiene el texto del prompt
        if not prompt.strip():
            messagebox.showwarning("Entrada vacía", "Por favor, escribe una descripción antes de generar el código.")
            return

        keywords = extract_keywords(prompt)
        print(keywords)
        
        # Generar código en base al prompt
        code = generate_code(keywords)
        if code is None:
            messagebox.showerror("Error", "No se pudo generar el código. Verifica la conexión o la API key.")
            return

        # Guardar el código generado en una variable
        self.generated_code = code

        # Mostrar el código generado en el área de salida
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", code)
        self.output.config(state="disabled")
        self.save_button.pack(pady=10)

        # Insertar en la base de datos MongoDB
        self.save_to_mongodb(prompt, keywords, code)

    def save_code_to_file(self):
        """Guarda el código generado en un archivo 'code.cpp' dentro de una carpeta llamada 'generated_code'."""
        if not self.generated_code:
            messagebox.showwarning("Código no generado", "Primero genera el código antes de guardarlo.")
            return

        # Definir la carpeta y el archivo
        folder_path = "generated_code"
        file_path = os.path.join(folder_path, "code.cpp")

        # Crear la carpeta si no existe
        os.makedirs(folder_path, exist_ok=True)

        # Guardar el código en el archivo
        try:
            with open(file_path, "w") as file:
                file.write(self.generated_code)
            messagebox.showinfo("Archivo Guardado", f"El código se ha guardado en '{file_path}'")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

    def save_to_mongodb(self, prompt, keywords, generated_code):
        """Inserta la información en la colección MongoDB."""
        try:
            document = {
                "prompt": prompt,
                "keywords": keywords,
                "generated_code": generated_code,
                "timestamp": datetime.utcnow()
            }
            collection.insert_one(document)
            print("Inserción exitosa en MongoDB")
        except Exception as e:
            print(f"Error al insertar en MongoDB: {e}")

    def run(self):
        """Ejecuta la interfaz gráfica."""
        self.root.mainloop()
