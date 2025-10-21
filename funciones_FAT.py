import json
import os 
import hashlib
from datetime import datetime

def encriptar_clave(clave):
    return hashlib.sha256(clave.encode("utf-8")).hexdigest()

class Usuario:
    def __init__(self,nombre, clave ,rol):
        self.nombre = nombre
        self.__clave = clave
        self.rol = rol
    @property
    def clave(self):
        return self.__clave
    
    def verificar_contrasena(self, intento):
        return self.__clave == encriptar_clave(intento)
    
    def convertir_a_diccionario(self):
        return {
            "nombre": self.nombre,
            "clave": self.__clave,
            "rol": self.rol
        }
    def validar_permiso(self, accion):
        permisos = {
            "admin": ["leer", "escribir", "eliminar", "crear usuario"],
            "usuario": ["leer", "escribir"],
            "invitado": ["leer"]
        }
        permisos_usuario = permisos.get(self.rol, [])

        if accion in permisos_usuario:
            return True
        else:
            return False



    
class Gestion_Usuarios:
    def __init__(self):
        self.usuarios = []

    def crear_usuario(self, usuario_actual, nombre, clave, rol):
        if not usuario_actual.validar_permiso("crear usuario"):
            print(f"El usuario '{usuario_actual.nombre}' no tiene permiso para crear usuarios.")
            return

        clave_encriptada = encriptar_clave(clave)
        nuevo_usuario = Usuario(nombre, clave_encriptada, rol)
        self.usuarios.append(nuevo_usuario)

        usuarios_existentes = []
        if os.path.exists("usuarios.json"):
            with open("usuarios.json", "r", encoding="utf-8") as archivo:
                try:
                    usuarios_existentes = json.load(archivo)
                except json.JSONDecodeError:
                    usuarios_existentes = []

        usuarios_existentes.append(nuevo_usuario.convertir_a_diccionario())

        with open("usuarios.json", "w", encoding="utf-8") as archivo:
            json.dump(usuarios_existentes, archivo, indent=4, ensure_ascii=False)


    def cargar_usuarios(self):
        if os.path.exists("usuarios.json"):
            with open("usuarios.json", "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                for d in datos:
                    usuario = Usuario(d["nombre"], d["clave"], d["rol"])
                    self.usuarios.append(usuario)
    
    def autenticar(self, nombre, intento):
        for u in self.usuarios:
            if u.nombre == nombre:
                return u.verificar_contrasena(intento)
        return False

class ArchivoLogico:
    def __init__(self,nombre, ruta, estado_papelera, cantidad_caracteres, fecha_creacion, fecha_modificacion, fecha_eliminacion, permisos):
        self.nombre = nombre
        self.ruta = ruta
        self.estado_papelera = estado_papelera
        self.cantidad_caracteres = cantidad_caracteres
        self.fecha_creacion = fecha_creacion
        self.fecha_modificacion = fecha_modificacion
        self.fecha_eliminacion = fecha_eliminacion
        self.permisos = permisos

    def convertir_a_diccionario(self):
        return {
            "nombre": self.nombre,
            "ruta": self.ruta,
            "estado": self.estado_papelera,
            "caracteres": self.cantidad_caracteres,
            "fecha de creacion": self.fecha_creacion,
            "fecha de modifiacion": self.fecha_modificacion,
            "fecha de elminiacion": self.fecha_eliminacion,
            "permisos": self.permisos
        }
class ArchivoFisico:
    def __init__(self, datos, siguiente, eof):
        self.datos = datos
        self.siguiente = siguiente
        self.eof = eof
    def convertir_a_diccionario(self):
        return {
            "datos": self.datos,
            "siguiente": self.siguiente,
            "eof": self.eof
        }
    


class GestionFAT:
    def __init__(self):
        self.archivos_logicos = []
        os.makedirs("bloques", exist_ok=True) 

    def crear_bloques_fisicos(self, nombre_archivo, contenido):
        # Divide el contenido en partes de máximo 20 caracteres
        bloques = [contenido[i:i+20] for i in range(0, len(contenido), 20)]
        rutas = []

        # bloques físicos
        for i, datos in enumerate(bloques):
            nombre_bloque = f"bloques/{nombre_archivo}_bloque_{i+1}.json"

            if i < len(bloques) - 1:
                siguiente = f"bloques/{nombre_archivo}_bloque_{i+2}.json"
            else:
                siguiente = None  

            # eof indica si es el último bloque del archivo
            if i == len(bloques) - 1:
                eof = True
            else:
                eof = False

            bloque = ArchivoFisico(datos, siguiente, eof)

            # Guardar el bloque en un archivo JSON
            with open(nombre_bloque, "w", encoding="utf-8") as f:
                json.dump(bloque.convertir_a_diccionario(), f, indent=4, ensure_ascii=False)

            rutas.append(nombre_bloque)

        # Retorna el bloque inicial
        if len(rutas) > 0:
            return rutas[0]
        else:
            return None

    def crear_archivo(self, usuario_actual, nombre, contenido=""):
        if not usuario_actual.validar_permiso("escribir"):
            print(f"El usuario '{usuario_actual.nombre}' no tiene permiso para crear archivos.")
            return
        
        for a in self.archivos_logicos:
            if a.nombre == nombre:
                return

        ruta_inicial = self.crear_bloques_fisicos(nombre, contenido)
        estado_papelera = False
        cantidad_caracteres = len(contenido)
        fecha_actual = datetime.now().isoformat()
        permisos = ["lectura", "escritura"]

        nuevo_archivo_logico = ArchivoLogico(nombre, ruta_inicial, estado_papelera, cantidad_caracteres,fecha_actual, fecha_actual, "", permisos)
        self.archivos_logicos.append(nuevo_archivo_logico)

        archivos_existentes = []
        if os.path.exists("tablas_FAT.json"):
            with open("tablas_FAT.json", "r", encoding="utf-8") as archivo:
                try:
                    archivos_existentes = json.load(archivo)
                except json.JSONDecodeError:
                    archivos_existentes = []

        archivos_existentes.append(nuevo_archivo_logico.convertir_a_diccionario())

        with open("tablas_FAT.json", "w", encoding="utf-8") as archivo:
            json.dump(archivos_existentes, archivo, indent=4, ensure_ascii=False)

    def leer_archivo(self, usuario_actual, nombre):
        if not usuario_actual.validar_permiso("leer"):
            print(f"El usuario '{usuario_actual.nombre}' no tiene permiso para leer archivos.")
            return None
        archivo = None
        for a in self.archivos_logicos:
            if a.nombre == nombre:
                archivo = a
                break

        if archivo is None:
            return  # No existe

        contenido_total = ""
        ruta = archivo.ruta

        # Lee todos los bloques encadenados
        while ruta:
            with open(ruta, "r", encoding="utf-8") as f:
                bloque = json.load(f)
                contenido_total += bloque["datos"]
                ruta = bloque["siguiente"]

        return contenido_total

    def modificar_archivo(self, usuario_actual, nombre, nuevo_contenido):
        if not usuario_actual.validar_permiso("escribir"):
            print(f"El usuario '{usuario_actual.nombre}' no tiene permiso para modificar archivos.")
            return
        
        archivo = None
        for a in self.archivos_logicos:
            if a.nombre == nombre:
                archivo = a
                break

        if archivo is None:
            return  

        ruta = archivo.ruta
        while ruta:
            if os.path.exists(ruta):
                with open(ruta, "r", encoding="utf-8") as f:
                    bloque = json.load(f)
                    ruta_siguiente = bloque["siguiente"]
                os.remove(ruta)
                ruta = ruta_siguiente
            else:
                ruta = None

        nueva_ruta = self.crear_bloques_fisicos(nombre, nuevo_contenido)
        archivo.ruta = nueva_ruta
        archivo.cantidad_caracteres = len(nuevo_contenido)
        archivo.fecha_modificacion = datetime.now().isoformat()

        self._guardar_tabla_fat()

    def _guardar_tabla_fat(self):
        datos = [a.convertir_a_diccionario() for a in self.archivos_logicos]
        with open("tablas_FAT.json", "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)

    def cargar_archivos(self):
        if os.path.exists("tablas_FAT.json"):
            with open("tablas_FAT.json", "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                for d in datos:
                    archivo_logico = ArchivoLogico(
                        d["nombre"], d["ruta"], d["estado"], d["caracteres"],
                        d["fecha de creacion"], d["fecha de modificacion"],
                        d["fecha de eliminacion"], d["permisos"]
                    )
                    self.archivos_logicos.append(archivo_logico)

