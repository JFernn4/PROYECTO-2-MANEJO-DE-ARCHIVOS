import json
import os 

class Usuario:
    def __init__(self,nombre, clave ,rol):
        self.nombre = nombre
        self.__clave = clave
        self.permiso = rol
    @property
    def clave(self):
        return self.__clave
    
    def verificar_contrasena(self, intento):
        return self.__clave == intento
    
    def convertir_a_diccionario(self):
        return {
            "nombre": self.nombre,
            "clave": self.__clave,
            "permiso": self.permiso
        }
    
class Gestion_Usuarios:
    def __init__(self):
        self.usuarios = []
        self.permisos = {
        "admin": ["leer","escribir","eliminar","crear usuario"],
        "usuario": ["leer","escribir"],
        "invitado": ["leer"]
        }


    def crear_usuario(self,nombre, clave, rol):
        nuevo_usuario = Usuario(nombre,clave,rol)
        self.usuarios.append(nuevo_usuario)

        datos_para_serializar = [u.convertir_a_diccionario() for u in self.usuarios]

        with open("usuarios.json","w",encoding="utf-8") as archivo:
            json.dump(datos_para_serializar, archivo, indent=4, ensure_ascii=False)

    def cargar_usuarios(self):
        if os.path.exists("usuarios.json"):
            with open("usuarios.json", "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                for d in datos:
                    usuario = Usuario(d["nombre"], d["clave"], d["permiso"])
                    self.usuarios.append(usuario)
    
    def autenticar(self, nombre, intento):
        for u in self.usuarios:
            if u.nombre == nombre:
                return u.verificar_contrasena(intento)
        return False



