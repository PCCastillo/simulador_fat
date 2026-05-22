#librerias con funciones que necesitamos
import threading #manejar hilos
import os #utilidades del sistema operativo
import time #manejar el tiempo
FILE="FILE"
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

#comando mkdir para crear directorios
def cmd_mkdir(nombre_directorio):
    registros = leer_registros() #llamamos a la funcion para leer los registros
    for r in registros: #nos movemos entre los registros
        if r["padre"] == GPWD and r["nombre"] == nombre_directorio: #busca algun directorio con el mismo nombre
            print(f"Error: El directorio o archivo '{nombre_directorio}' ya existe.")
            return #se va
    nuevo_id = obtener_siguiente_id(registros) #obtiene el siguiente id
    escribir_registro(nuevo_id, nombre_directorio, "DIR", GPWD, "rwx", 0) #escribe nuevo directorio con los parametros dados
    print(f"Directorio '{nombre_directorio}' creado correctamente.") #confirma la creacion

#comando ls para mostrar registros
def cmd_ls():
    registros = leer_registros() #llama a la funcion para leer
    encontrados = [r["nombre"] for r in registros if r["padre"] == GPWD] #guarda todos los encontrados en un arreglo para imprimir
    if encontrados:
        for nombre in encontrados:
            print(nombre) #imprime los elementos
    else:
        print("(Directorio vacío)") #si esta vacio

#comando cd para navegar entre directorios
def cmd_cd(destino):
    global GPWD #tomamos la variable que contiene donde estamos parados
    registros = leer_registros() #leemos los registros en registros
    
    if destino == "..": #para ir a un dirctorio superior
        if GPWD == 0:
            print("Ya te encuentras en el directorio raíz (/).")
            return
        for r in registros: 
            if r["id"] == GPWD:
                GPWD = r["padre"] #cambiamos nuestro lugar al directorio padre
                print(f"Directorio actual cambiado a: {obtener_ruta_actual()}")
                return
    else:
        for r in registros: #ahora iteramos  sobre los registros
            if r["padre"] == GPWD and r["nombre"] == destino and r["tipo"] == "DIR": #si padre coincide, nombre y tipo, cambiamos
                GPWD = r["id"]
                print(f"Directorio actual cambiado a: {obtener_ruta_actual()}")
                return
        print(f"Error: El directorio '{destino}' no existe en la ubicación actual.")

#para obtener la ruta actual en la que estamos
def obtener_ruta_actual():
    if GPWD == 0: #si nos encontramos en la raiz
        return "/"
    registros = leer_registros() #lee registros
    id_actual = GPWD #toma el lugar actual donde estamos
    ruta = "" #inicializamos la ruta
    while id_actual != 0: #mientras que no lleguemos a la raiz no nos detenemos
        for r in registros: #iteramos en registros
            if r["id"] == id_actual: #si  el id del registro actual es  guarda el nombre
                ruta = "/" + r["nombre"] + ruta  #guardamos junto a la ruta anterior
                id_actual = r["padre"] #nos movemos de directorio
                break
    return ruta

#touch para crear
def cmd_touch(nombre_archivo):
    with file_lock:
        registros = leer_registros_sin_lock()
        for r in registros:
            if r["padre"] == GPWD and r["nombre"] == nombre_archivo: #si ya existe un archivo dentro del dir
                print(f"Error: El archivo o directorio '{nombre_archivo}' ya existe.")
                return
        nuevo_id = obtener_siguiente_id(registros)
        with open(DATABASE_FILE, "a", encoding="utf-8") as f: #abre para anexar a
            f.write(f"{nuevo_id}|{nombre_archivo}|{FILE}|{GPWD}|rw-|10\n") #nuevo registro en el formato
    print(f"Archivo '{nombre_archivo}' creado correctamente.") #confirma

#ls detallado
def cmd_ls_1():
    registros = leer_registros()
    hijos = [r for r in registros if r["padre"] == GPWD]
    
    print("ID\tTIPO\tPERMISOS | TAMAÑO | NOMBRE")
    for r in hijos:
        print(f"{r['id']}\t{r['tipo']}\t{r['permisos']}      | {r['tamaño']}     | {r['nombre']}")



#flujo principal
def main():
    global GPWD #avisamos que vamos a usar la variable de donde estamos parados
    inicializar_sistema()

    #encabezado basico
    print("====================")
    print("SIMULADOR FAT EN PYTHON")
    print("====================")
    print("Sistema FAT inicializado correctamente.")
    print("Comandos: mkdir, ls, cd")
    print("Directorio actual: /")

    while True: #bucle infinito, para que no se cierre solito
        try: #capturamos posibles errores o interrupciones de teclado
            entrada = input("\n> ").strip().split() #mostramos el indicador de la consola, borramos los espacios en blanco accidentales
            #y dividimos la cadena en palabras individuales
        except (KeyboardInterrupt, EOFError): #captura si el usuario  fuerza la salida
            print("\nSaliendo del simulador FAT...") #mensajito
            break #finaliza la ejecucion

        if not entrada: #si la lista de entrada esta vacia (solo apretamos enter)
            continue #regresa al inicio del bucle

        comando = entrada[0] #almacena el primer elemento de la lista en la variable

        if comando == "exit": #si ponemos el comando de salida
            print("Saliendo del simulador FAT...")
            break

        elif comando == "mkdir":
            if len(entrada) < 2:
                print("Error: Falta especificar el nombre del directorio.")
            else:
                cmd_mkdir(entrada[1])

        elif comando == "ls":
            if len(entrada) > 1 and entrada[1] == "-1":
                cmd_ls_1()
            else:
                cmd_ls()

        elif comando == "cd":
            if len(entrada) < 2:
                GPWD = 0
                print("Directorio actual cambiado a: /")
            else:
                cmd_cd(entrada[1])

        elif comando == "touch":
            if len(entrada) < 2:
                print("Error: Falta especificar el nombre del archivo.")
            else:
                cmd_touch(entrada[1])

        else: #si ponemos cualquier otra cosa
            print("Comando no reconocido o no implementado aún.")

#ejecucion
if __name__ == "__main__":
    main()
