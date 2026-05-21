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
