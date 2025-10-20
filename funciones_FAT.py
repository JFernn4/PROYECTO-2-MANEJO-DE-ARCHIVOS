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
    
class Gestion_Usuarios:
    def __init__(self):
        self.usuarios = []
        self.permisos = {
        "admin": ["leer","escribir","eliminar","crear usuario"],
        "usuario": ["leer","escribir"],
        "invitado": ["leer"]
        }

    def crear_usuario(self, nombre, clave, rol):
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

class GestionFAT:
    def __init__(self):
        self.archivos_logicos = []

    def crear_archivo(self, nombre):
        if any(a.nombre == nombre for a in self.archivos_logicos):
            print(f"El archivo '{nombre}' ya existe.")
            return

        ruta = "archivos/" + nombre
        estado_papelera = False
        cantidad_caracteres = 0
        fecha_creacion = datetime.now().isoformat()
        fecha_modificacion = datetime.now().isoformat()
        fecha_eliminacion = ""
        permisos = ["lectura", "escritura"]
        nuevo_archivo_logico = ArchivoLogico(nombre, ruta, estado_papelera, cantidad_caracteres, fecha_creacion, fecha_modificacion, fecha_eliminacion, permisos)
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
    
    def cargar_archivos(self):
        if os.path.exists("tablas_FAT.json"):
            with open("tablas_FAT.json", "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                for d in datos:
                    archivo_logico = ArchivoLogico(d["nombre"], d["ruta"], d["estado"],d["caracteres"],d["fecha de creacion"],d["fecha de modificacion"],d["fecha de eliminacion"], d["permisos"])
                    self.archivos_logicos.append(archivo_logico)


gestion = GestionFAT()
gestion.cargar_archivos()
gestion.crear_archivo("prueba.txt")



