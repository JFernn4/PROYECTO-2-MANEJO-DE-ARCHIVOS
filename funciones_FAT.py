import json
import os 
import shutil
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
        self.usuarios = []  # Limpiar lista antes de cargar
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
            "fecha_creacion": self.fecha_creacion,
            "fecha_modificacion": self.fecha_modificacion,
            "fecha_eliminacion": self.fecha_eliminacion,
            "permisos": self.permisos
        }
    def mostrar_metadatos(self):
        return {
            "Nombre": self.nombre,
            "Ruta": self.ruta,
            "En papelera": "Sí" if self.estado_papelera else "No",
            "Tamaño (caracteres)": self.cantidad_caracteres,
            "Fecha de creación": self.fecha_creacion,
            "Fecha de modificación": self.fecha_modificacion,
            "Fecha de eliminación": self.fecha_eliminacion if self.fecha_eliminacion else "N/A",
            "Permisos": ", ".join(self.permisos)
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
        self.papelera = []
        os.makedirs("bloques", exist_ok=True) 
        os.makedirs("papelera_bloques", exist_ok=True) 
        self.migrar_archivo_json()  
        self.cargar_archivos()

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
            if a.nombre == nombre and not a.estado_papelera:
                print(f"Ya existe un archivo con el nombre '{nombre}'")
                return

        ruta_inicial = self.crear_bloques_fisicos(nombre, contenido)
        estado_papelera = False
        cantidad_caracteres = len(contenido)
        fecha_actual = datetime.now().isoformat()
        permisos = ["lectura", "escritura"]

        nuevo_archivo_logico = ArchivoLogico(nombre, ruta_inicial, estado_papelera, cantidad_caracteres,
                                            fecha_actual, fecha_actual, "", permisos)
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
        # Guardar solo archivos que no están en la papelera
        archivos_activos = [a for a in self.archivos_logicos if not a.estado_papelera]
        datos = [a.convertir_a_diccionario() for a in archivos_activos]
        with open("tablas_FAT.json", "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)

    def cargar_archivos(self):
        self.archivos_logicos = []  # Limpiar lista antes de cargar
        if os.path.exists("tablas_FAT.json"):
            with open("tablas_FAT.json", "r", encoding="utf-8") as archivo:
                try:
                    datos = json.load(archivo)
                    for d in datos:
                        # SOLO cargar archivos que NO están en papelera
                        if not d.get("estado", False):  # estado_papelera = False
                            archivo_logico = ArchivoLogico(
                                d["nombre"], d["ruta"], d["estado"], d["caracteres"],
                                d["fecha_creacion"], d["fecha_modificacion"],
                                d["fecha_eliminacion"], d["permisos"]
                            )
                            self.archivos_logicos.append(archivo_logico)
                except json.JSONDecodeError:
                    pass  # Si el archivo está vacío
        
        # También cargar la papelera desde papelera.json
        self.cargar_papelera_desde_json()

    def cargar_papelera_desde_json(self):
        self.papelera = []  # Limpiar papelera actual
        if os.path.exists("papelera.json"):
            with open("papelera.json", "r", encoding="utf-8") as archivo:
                try:
                    datos = json.load(archivo)
                    for d in datos:
                        archivo_logico = ArchivoLogico(
                            d["nombre"], d["ruta"], d["estado"], d["caracteres"],
                            d["fecha_creacion"], d["fecha_modificacion"],
                            d["fecha_eliminacion"], d["permisos"]
                        )
                        self.papelera.append(archivo_logico)
                except json.JSONDecodeError:
                    pass  # Si el archivo está vacío o corrupto

    def eliminar_archivo(self, usuario_actual, nombre):
        if not usuario_actual.validar_permiso("eliminar"):
            print(f"El usuario '{usuario_actual.nombre}' no tiene permiso para eliminar archivos.")
            return
        
        archivo_a_eliminar = None
        for a in self.archivos_logicos:
            if a.nombre == nombre:
                archivo_a_eliminar = a
                break

        if archivo_a_eliminar is None:
            print(f"No se encontró el archivo '{nombre}'.")
            return

        ruta = archivo_a_eliminar.ruta
        while ruta:
            if os.path.exists(ruta):
                nombre_bloque = os.path.basename(ruta)
                nueva_ruta = os.path.join("papelera_bloques", nombre_bloque)
                shutil.move(ruta, nueva_ruta)  # mueve el bloque
                
                # ACTUALIZAR: Cambiar la ruta en el objeto archivo para que apunte a papelera_bloques
                if ruta == archivo_a_eliminar.ruta:  # Si es el primer bloque
                    archivo_a_eliminar.ruta = nueva_ruta
                    ruta = nueva_ruta
                
                with open(nueva_ruta, "r", encoding="utf-8") as f:
                    bloque = json.load(f)
                    ruta = bloque["siguiente"]
            else:
                ruta = None

        archivo_a_eliminar.estado_papelera = True
        archivo_a_eliminar.fecha_eliminacion = datetime.now().isoformat()
        self.archivos_logicos.remove(archivo_a_eliminar)
        self.papelera.append(archivo_a_eliminar)

        # Guardar en papelera.json
        papelera_existente = []
        if os.path.exists("papelera.json"):
            with open("papelera.json", "r", encoding="utf-8") as archivo:
                try:
                    papelera_existente = json.load(archivo)
                except json.JSONDecodeError:
                    papelera_existente = []

        papelera_existente.append(archivo_a_eliminar.convertir_a_diccionario())
        with open("papelera.json", "w", encoding="utf-8") as archivo:
            json.dump(papelera_existente, archivo, indent=4, ensure_ascii=False)
        
        # Actualizar la tabla FAT (eliminar el archivo de archivos activos)
        self._guardar_tabla_fat()
        
    def recuperar_archivo(self, nombre):
        archivo_a_recuperar = None
        for a in self.papelera:
            if a.nombre == nombre:
                archivo_a_recuperar = a
                break

        if archivo_a_recuperar is None:
            print(f"No se encontró el archivo '{nombre}' en la papelera.")
            return

        # Mover bloques de papelera_bloques a bloques/
        ruta = archivo_a_recuperar.ruta
        
        #Actualizar la ruta para apuntar a papelera_bloques
        if ruta and "papelera_bloques" not in ruta:
            nombre_bloque_base = os.path.basename(ruta)
            ruta = os.path.join("papelera_bloques", nombre_bloque_base)
        
        bloques_actualizados = []

        while ruta:
            if os.path.exists(ruta):
                nombre_bloque = os.path.basename(ruta)
                ruta_recuperada = os.path.join("bloques", nombre_bloque)
                shutil.move(ruta, ruta_recuperada)  # mueve el bloque a la carpeta original
                bloques_actualizados.append(ruta_recuperada)

                # Leer siguiente bloque
                with open(ruta_recuperada, "r", encoding="utf-8") as f:
                    bloque = json.load(f)
                    ruta = bloque["siguiente"]
                    # CORRECIÓN: Actualizar también la siguiente ruta si es necesario
                    if ruta and "papelera_bloques" not in ruta:
                        nombre_bloque_siguiente = os.path.basename(ruta)
                        ruta = os.path.join("papelera_bloques", nombre_bloque_siguiente)
            else:
                ruta = None

        # Actualizar ruta inicial del archivo lógico
        archivo_a_recuperar.ruta = bloques_actualizados[0] if bloques_actualizados else None
        archivo_a_recuperar.estado_papelera = False
        archivo_a_recuperar.fecha_eliminacion = ""

        # Mover de la lista de papelera a archivos activos
        self.papelera.remove(archivo_a_recuperar)
        self.archivos_logicos.append(archivo_a_recuperar)

        # Actualizar papelera.json
        papelera_actual = []
        if os.path.exists("papelera.json"):
            with open("papelera.json", "r", encoding="utf-8") as archivo:
                try:
                    papelera_actual = json.load(archivo)
                except json.JSONDecodeError:
                    papelera_actual = []

        papelera_actual = [p for p in papelera_actual if p["nombre"] != nombre]
        with open("papelera.json", "w", encoding="utf-8") as archivo:
            json.dump(papelera_actual, archivo, indent=4, ensure_ascii=False)

        # Guardar la tabla FAT actualizada
        self._guardar_tabla_fat()

    def migrar_archivo_json(self):
        if os.path.exists("tablas_FAT.json"):
            with open("tablas_FAT.json", "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            
            # Actualizar las claves
            for dato in datos:
                if "fecha de modifiacion" in dato:
                    dato["fecha_modificacion"] = dato.pop("fecha de modifiacion")
                if "fecha de creacion" in dato:
                    dato["fecha_creacion"] = dato.pop("fecha de creacion")
                if "fecha de eliminacion" in dato:
                    dato["fecha_eliminacion"] = dato.pop("fecha de eliminacion")
                if "fecha de elminiacion" in dato:
                    dato["fecha_eliminacion"] = dato.pop("fecha de elminiacion")
            
            # Guardar con las nuevas claves
            with open("tablas_FAT.json", "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, indent=4, ensure_ascii=False)



        

