#librerias con funciones que necesitamos
import threading #manejar hilos
import os #utilidades del sistema operativo
import time #manejar el tiempo

DATABASE_FILE = "fat_db.txt" #nombre del archivo que guarda la base de datos del fat
GPWD = 0  #lleva el control de donde estamos parados
file_lock = threading.Lock() #obliga a que los hilos pueda hacer una sola tarea a la vez

#se encarga de preparar el entorno antes de recibir comandos
def inicializar_sistema():
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "w", encoding="utf-8") as f: #abre o crea el archivo en modo escritura w
            # ID | NOMBRE | TIPO | PADRE | PERMISOS | TAMAÑO
            f.write("0|/|DIR|-1|rwx|0\n")

#lee el archivo linea por linea y transforma de texto plano a un diccionario
def leer_registros_sin_lock():
    registros = [] #aqui se guarda todos los archivos y directorios recuperados de la db
    if not os.path.exists(DATABASE_FILE): #si no exist, devuelve la lista vacia para evitar errores
        return registros
    with open(DATABASE_FILE, "r", encoding="utf-8") as f: #abre en modo lectura r
        for linea in f: #linea por linea
            linea = linea.strip() #borramos los espacios en blanco y el salto de linea
            if linea: #verificamos que no este vacia para romper la cadena de texto con | como separador
                partes = linea.split("|")
                registros.append({ #agrega un nuevo diccionario donde se insertan los datos
                    "id": int(partes[0]),
                    "nombre": partes[1],
                    "tipo": partes[2],
                    "padre": int(partes[3]),
                    "permisos": partes[4],
                    "tamaño": int(partes[5])
                })
    return registros #devuelve la lista completa

#lee todos los registros de archivo de forma segura
def leer_registros():
    with file_lock:
        return leer_registros_sin_lock()

#se encarga de guadar los nuevos elementos
def escribir_registro(id_reg, nombre, tipo, padre, permisos, tamaño):
    with file_lock:
        with open(DATABASE_FILE, "a", encoding="utf-8") as f: #abre archivo en modo anexar a para no borrar contenido previo
            f.write(f"{id_reg}|{nombre}|{tipo}|{padre}|{permisos}|{tamaño}\n") #ingresa en el formato

#como debe ser ordenado, cada elemento necesita un ID, aqui calculamos el siguiente que le toca al nuevo
def obtener_siguiente_id(registros):
    if not registros:
        return 0
    return max(r["id"] for r in registros) + 1 #encuentra el mas alto y se suma 1 para que el mas reciente tenga el mas alto

#flujo principal
def main():
    global GPWD #avisamos que vamos a usar la variable de donde estamos parados
    inicializar_sistema()

    #encabezado basico
    print("====================")
    print("SIMULADOR FAT EN PYTHON")
    print("====================")
    print("Sistema FAT inicializado correctamente.")
    print("Directorio actual: /")

#ejecucion
if __name__ == "__main__":
    main()
