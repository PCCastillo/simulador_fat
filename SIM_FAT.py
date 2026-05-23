# librerias con funciones que necesitamos
import threading  # manejar hilos
import os  # utilidades del sistema operativo
import time  # manejar el tiempo
FILE = "FILE"
DATABASE_FILE = "fat_db.txt"  # nombre del archivo que guarda la base de datos del fat
GPWD = 0  # lleva el control de donde estamos parados
# obliga a que los hilos pueda hacer una sola tarea a la vez
file_lock = threading.Lock()

# se encarga de preparar el entorno antes de recibir comandos


def inicializar_sistema():
    if not os.path.exists(DATABASE_FILE):
        # abre o crea el archivo en modo escritura w
        with open(DATABASE_FILE, "w", encoding="utf-8") as f:
            # ID | NOMBRE | TIPO | PADRE | PERMISOS | TAMAÑO
            f.write("0|/|DIR|-1|rwx|0\n")

# lee el archivo linea por linea y transforma de texto plano a un diccionario


def leer_registros_sin_lock():
    registros = []  # aqui se guarda todos los archivos y directorios recuperados de la db
    # si no exist, devuelve la lista vacia para evitar errores
    if not os.path.exists(DATABASE_FILE):
        return registros
    with open(DATABASE_FILE, "r", encoding="utf-8") as f:  # abre en modo lectura r
        for linea in f:  # linea por linea
            linea = linea.strip()  # borramos los espacios en blanco y el salto de linea
            if linea:  # verificamos que no este vacia para romper la cadena de texto con | como separador
                partes = linea.split("|")
                registros.append({  # agrega un nuevo diccionario donde se insertan los datos
                    "id": int(partes[0]),
                    "nombre": partes[1],
                    "tipo": partes[2],
                    "padre": int(partes[3]),
                    "permisos": partes[4],
                    "tamaño": int(partes[5])
                })
    return registros  # devuelve la lista completa

# lee todos los registros de archivo de forma segura


def leer_registros():
    with file_lock:
        return leer_registros_sin_lock()

# se encarga de guadar los nuevos elementos


def escribir_registro(id_reg, nombre, tipo, padre, permisos, tamaño):
    with file_lock:
        # abre archivo en modo anexar a para no borrar contenido previo
        with open(DATABASE_FILE, "a", encoding="utf-8") as f:
            # ingresa en el formato
            f.write(f"{id_reg}|{nombre}|{tipo}|{padre}|{permisos}|{tamaño}\n")

# como debe ser ordenado, cada elemento necesita un ID, aqui calculamos el siguiente que le toca al nuevo


def obtener_siguiente_id(registros):
    if not registros:
        return 0
    # encuentra el mas alto y se suma 1 para que el mas reciente tenga el mas alto
    return max(r["id"] for r in registros) + 1

# comando mkdir para crear directorios


def cmd_mkdir(nombre_directorio):
    registros = leer_registros()  # llamamos a la funcion para leer los registros
    for r in registros:  # nos movemos entre los registros
        # busca algun directorio con el mismo nombre
        if r["padre"] == GPWD and r["nombre"] == nombre_directorio:
            print(
                f"Error: El directorio o archivo '{nombre_directorio}' ya existe.")
            return  # se va
    nuevo_id = obtener_siguiente_id(registros)  # obtiene el siguiente id
    # escribe nuevo directorio con los parametros dados
    escribir_registro(nuevo_id, nombre_directorio, "DIR", GPWD, "rwx", 0)
    # confirma la creacion
    print(f"Directorio '{nombre_directorio}' creado correctamente.")

# comando ls para mostrar registros


def cmd_ls():
    registros = leer_registros()  # llama a la funcion para leer
    # guarda todos los encontrados en un arreglo para imprimir
    encontrados = [r["nombre"] for r in registros if r["padre"] == GPWD]
    if encontrados:
        for nombre in encontrados:
            print(nombre)  # imprime los elementos
    else:
        print("(Directorio vacío)")  # si esta vacio

# comando cd para navegar entre directorios


def cmd_cd(destino):
    global GPWD  # tomamos la variable que contiene donde estamos parados
    registros = leer_registros()  # leemos los registros en registros

    if destino == "..":  # para ir a un dirctorio superior
        if GPWD == 0:
            print("Ya te encuentras en el directorio raíz (/).")
            return
        for r in registros:
            if r["id"] == GPWD:
                # cambiamos nuestro lugar al directorio padre
                GPWD = r["padre"]
                print(f"Directorio actual cambiado a: {obtener_ruta_actual()}")
                return
    else:
        for r in registros:  # ahora iteramos  sobre los registros
            # si padre coincide, nombre y tipo, cambiamos
            if r["padre"] == GPWD and r["nombre"] == destino and r["tipo"] == "DIR":
                GPWD = r["id"]
                print(f"Directorio actual cambiado a: {obtener_ruta_actual()}")
                return
        print(
            f"Error: El directorio '{destino}' no existe en la ubicación actual.")

# para obtener la ruta actual en la que estamos


def obtener_ruta_actual():
    if GPWD == 0:  # si nos encontramos en la raiz
        return "/"
    registros = leer_registros()  # lee registros
    id_actual = GPWD  # toma el lugar actual donde estamos
    ruta = ""  # inicializamos la ruta
    while id_actual != 0:  # mientras que no lleguemos a la raiz no nos detenemos
        for r in registros:  # iteramos en registros
            if r["id"] == id_actual:  # si  el id del registro actual es  guarda el nombre
                # guardamos junto a la ruta anterior
                ruta = "/" + r["nombre"] + ruta
                id_actual = r["padre"]  # nos movemos de directorio
                break
    return ruta

# touch para crear


def cmd_touch(nombre_archivo):
    with file_lock:
        registros = leer_registros_sin_lock()
        for r in registros:
            # si ya existe un archivo dentro del dir
            if r["padre"] == GPWD and r["nombre"] == nombre_archivo:
                print(
                    f"Error: El archivo o directorio '{nombre_archivo}' ya existe.")
                return
        nuevo_id = obtener_siguiente_id(registros)
        with open(DATABASE_FILE, "a", encoding="utf-8") as f:  # abre para anexar a
            # nuevo registro en el formato
            f.write(f"{nuevo_id}|{nombre_archivo}|{FILE}|{GPWD}|rw-|10\n")
    print(f"Archivo '{nombre_archivo}' creado correctamente.")  # confirma

# ls detallado


def cmd_ls_l():
    registros = leer_registros()
    hijos = [r for r in registros if r["padre"] == GPWD]
    print("ID | TIPO | PERMISOS | TAMAÑO | NOMBRE")
    for r in hijos:
        print(f"{r['id']} | {r['tipo']} | {r['permisos']} | {r['tamaño']} | {r['nombre']}")

# actualizamos todo el archivo


def actualizar_archivo_completo(registros):
    with file_lock:
        with open(DATABASE_FILE, "w", encoding="utf-8") as f:
            for r in registros:
                f.write(
                    f"{r['id']}|{r['nombre']}|{r['tipo']}|{r['padre']}|{r['permisos']}|{r['tamaño']}\n")

# eliminar


def cmd_rm(nombre_archivo):
    registros = leer_registros()
    inicial_len = len(registros)
    # filtra excluyendo el archivo que hace match
    registros = [r for r in registros if not (
        r["padre"] == GPWD and r["nombre"] == nombre_archivo and r["tipo"] == "FILE")]
    if len(registros) < inicial_len:
        actualizar_archivo_completo(registros)
        print(f"Archivo '{nombre_archivo}' eliminado correctamente.")
    else:
        print(
            f"Error: El archivo '{nombre_archivo}' no existe o es un directorio.")

# chemod


def cmd_chmod(nuevos_permisos, nombre_objetivo):
    registros = leer_registros()  # obtenemos todos los registros
    modificado = False  # aun no se hace nada
    for r in registros:
        if r["padre"] == GPWD and r["nombre"] == nombre_objetivo:  # si coincide
            r["permisos"] = nuevos_permisos  # sobreescribimos los permisos
            modificado = True  # ahora si esta hacido
            break
    if modificado:
        actualizar_archivo_completo(registros)
        print(
            f"Permisos de '{nombre_objetivo}' cambiados a {nuevos_permisos}.")
    else:
        print(f"Error: No se encontró '{nombre_objetivo}' en este directorio.")

############################### -----HILOS-----########################################


def tarea_hilo(id_hilo):
    nombre_archivo = f"hilo_{id_hilo}.txt"
    print(f"Hilo {id_hilo} creando archivo {nombre_archivo}")
    cmd_touch(nombre_archivo)
    time.sleep(0.1)


def cmd_test_hilos():
    print("Iniciando prueba concurrente con hilos...")
    hilos = []
    for i in range(1, 6):
        t = threading.Thread(target=tarea_hilo, args=(i,))
        hilos.append(t)
        t.start()

    for t in hilos:
        t.join()

    print("Todos los hilos finalizaron correctamente.")

######################################################################################

# flujo principal

def cmd_help():
# encabezado basico
    print("====================")
    print("SIMULADOR FAT EN PYTHON")
    print("====================")
    print("Sistema FAT inicializado correctamente.")
    print("Comandos: mkdir, ls, cd, touch, rm y chmod")
    print("Para salir escriba: exit o Ctrl C")
    print("Directorio actual: /")

#main
def main():
    global GPWD  # avisamos que vamos a usar la variable de donde estamos parados
    inicializar_sistema()
    cmd_help()
    while True:  # bucle infinito, para que no se cierre solito
        try:  # capturamos posibles errores o interrupciones de teclado
            # mostramos el indicador de la consola, borramos los espacios en blanco accidentales
            entrada = input("\n> ").strip().split()
            # y dividimos la cadena en palabras individuales
        except (KeyboardInterrupt, EOFError):  # captura si el usuario  fuerza la salida
            print("\nSaliendo del simulador FAT...")  # mensajito
            break  # finaliza la ejecucion

        # si la lista de entrada esta vacia (solo apretamos enter)
        if not entrada:
            continue  # regresa al inicio del bucle

        # almacena el primer elemento de la lista en la variable
        comando = entrada[0]

        if comando == "exit":  # si ponemos el comando de salida
            print("Saliendo del simulador FAT...")
            break

        elif comando == "mkdir":
            if len(entrada) < 2:
                print("Error: Falta especificar el nombre del directorio.")
            else:
                cmd_mkdir(entrada[1])

        elif comando == "ls":
            if len(entrada) > 1 and entrada[1] == "-l":
                cmd_ls_l()
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

        elif comando == "rm":
            if len(entrada) < 2:
                print("Error: Falta especificar el archivo a eliminar.")
            else:
                cmd_rm(entrada[1])

        elif comando == "chmod":  # chemod jeje
            if len(entrada) < 3:
                print("Error: Formato requerido: chmod <permisos> <nombre>")
            else:
                cmd_chmod(entrada[1], entrada[2])
        # Inregación de hilo para prueba de concurrencia
        elif comando == "test_hilos":
            cmd_test_hilos()

        #comando help para mostrar ayuda
        elif comando == "help":
            cmd_help()

        else:  # si ponemos cualquier otra cosa
            print("Comando no reconocido o no implementado aún.")


# ejecucion
if __name__ == "__main__":
    main()
