import os
from openai import OpenAI
from dotenv import load_dotenv
from gui import CodeGenerator

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuración del cliente de OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_code(prompt):
    # Solicita la finalización del chat con el prompt adecuado
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "system", "content": "Eres un generador de código C++"},
            {"role": "user", "content": f"Genera código en C++ para lo siguiente: {prompt}."}
        ]
    )
    
    # Accede al contenido del mensaje generado por el modelo
    code = response.choices[0].message.content.strip()
    return code

def extract_key_words(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un extractor de palabras clave."},
            {"role": "user", "content": f"Clasifica las palabras clave del siguiente prompt en diferentes categorias: {prompt}"}
        ]
    )
    
    code = response.choices[0].message.content.strip()
    return code

def main():
    app = CodeGenerator()
    app.run()

if __name__ == "__main__":
    main()
