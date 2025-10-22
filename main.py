from funciones_FAT import Usuario, Gestion_Usuarios, GestionFAT, ArchivoLogico, ArchivoFisico
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import json
import os

# Tema proporcionado
tema = {
    "fondo_principal": "#F0F0F0",
    "fondo_menu": "#2f3136",
    "texto": "white",
    "texto2": "black",
    "seleccion": "#fc5e5b",
    "fuente": ("Century Gothic", 12)
}

# Clase principal de la aplicación
class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación sistema de archivos FAT")
        self.root.geometry("1280x720")
        self.root.configure(bg=tema["fondo_principal"])
        
        self.gestion = Gestion_Usuarios()
        self.gestion_FAT = GestionFAT()
        
        # Cargar datos existentes ANTES de verificar el admin
        self.gestion.cargar_usuarios()
        self.gestion_FAT.cargar_archivos()
        
        # Crear usuario admin si no existe
        if not any(u.nombre == "admin" for u in self.gestion.usuarios):
            # Crear admin con clave encriptada correctamente
            from funciones_FAT import encriptar_clave
            clave_encriptada = encriptar_clave("123")
            admin = Usuario("admin", clave_encriptada, "admin")
            self.gestion.usuarios.append(admin)
            self._guardar_usuarios()
        
        self.usuario_actual = None
        self.mostrar_login()
    
    def _guardar_usuarios(self):
        datos = [u.convertir_a_diccionario() for u in self.gestion.usuarios]
        with open("usuarios.json", "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)
    
    def mostrar_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.login_frame = tk.Frame(self.root, bg=tema["fondo_principal"])
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(self.login_frame, text="Iniciar Sesión", bg=tema["fondo_principal"], fg=tema["texto2"], font=(tema["fuente"][0], 16, "bold")).pack(pady=20)
        
        tk.Label(self.login_frame, text="Nombre:", bg=tema["fondo_principal"], fg=tema["texto2"], font=tema["fuente"]).pack()
        self.entry_nombre = tk.Entry(self.login_frame, font=tema["fuente"], width=20)
        self.entry_nombre.pack(pady=5)

        tk.Label(self.login_frame, text="Clave:", bg=tema["fondo_principal"], fg=tema["texto2"], font=tema["fuente"]).pack()
        self.entry_clave = tk.Entry(self.login_frame, show="*", font=tema["fuente"], width=20)
        self.entry_clave.pack(pady=5)
        
        # Bind Enter key to login
        self.entry_clave.bind('<Return>', lambda event: self.intentar_login())

        tk.Button(self.login_frame, text="Iniciar Sesión", bg=tema["seleccion"], fg=tema["texto"], 
                 font=tema["fuente"], command=self.intentar_login, width=15).pack(pady=20)
        
        # Poner foco en el primer campo
        self.entry_nombre.focus()
    
    def intentar_login(self):
        nombre = self.entry_nombre.get()
        clave = self.entry_clave.get()
        
        # Recargar usuarios por si hay cambios
        self.gestion.cargar_usuarios()

        if self.gestion.autenticar(nombre, clave):
            self.usuario_actual = next(u for u in self.gestion.usuarios if u.nombre == nombre)
            messagebox.showinfo("Éxito", f"Bienvenido, {self.usuario_actual.nombre}!")
            self.mostrar_interfaz_principal()
        else:
            messagebox.showerror("Error", "Nombre o clave incorrectos.")
            self.entry_clave.delete(0, tk.END)
            self.entry_clave.focus()
    
    def mostrar_interfaz_principal(self):
        self.login_frame.destroy()
        self.crear_frames()
        self.mostrar_inicio()
    
    def mostrar_inicio(self):
        # Limpiar frame central
        for widget in self.frame_central.winfo_children():
            widget.destroy()
        
        # Recrear elementos del frame central
        self.frame_superior_central = tk.Frame(self.frame_central, bg=tema["fondo_principal"], height=30)
        self.frame_superior_central.pack(side=tk.TOP, fill=tk.X)
        
        tk.Label(self.frame_superior_central, text="Lista de archivos", font=(tema["fuente"][0], 14),
                 fg=tema["texto2"], bg=tema["fondo_principal"]).pack(side=tk.LEFT, pady=15, padx=30)

        # Frame para la lista de archivos
        frame_lista = tk.Frame(self.frame_central, bg=tema["fondo_principal"])
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # Scrollbar para la lista
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.lista_archivos = tk.Listbox(frame_lista, font=tema["fuente"],
                                         selectbackground=tema["seleccion"],
                                         bg=tema["fondo_principal"], fg="black",
                                         yscrollcommand=scrollbar.set)
        self.lista_archivos.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.lista_archivos.yview)

        self.lista_archivos.bind("<Button-3>", self.mostrar_menu_contextual)
        
        # Frame para botones inferiores
        self.pie = tk.Frame(self.frame_central, bg=tema["fondo_principal"])
        self.pie.pack(fill=tk.X, pady=10)
        
        opciones_boton2 = {"width": 25, "font": tema["fuente"],
                          "bg": tema["fondo_menu"], "fg": "white",
                          "activebackground": "#d94e4c", "relief": "flat"}
        
        tk.Button(self.pie, text="Abrir seleccionado", command=self.abrir_archivo, **opciones_boton2).pack(side=tk.LEFT, padx=30, pady=15)
        tk.Button(self.pie, text="Modificar seleccionado", command=self.modificar_archivo, **opciones_boton2).pack(side=tk.LEFT, padx=30, pady=15)
        tk.Button(self.pie, text="Eliminar seleccionado", command=self.eliminar_archivo, **opciones_boton2).pack(side=tk.LEFT, padx=30, pady=15)
        
        # Actualizar lista de archivos
        self.actualizar_lista_archivos()
    
    def actualizar_lista_archivos(self):
        self.lista_archivos.delete(0, tk.END)
        # NO llamar a cargar_archivos aquí para evitar duplicados
        for archivo in self.gestion_FAT.archivos_logicos:
            if not archivo.estado_papelera:
                # Formatear fecha para mejor visualización
                fecha = archivo.fecha_modificacion[:16].replace('T', ' ') if archivo.fecha_modificacion else "N/A"
                linea = f"{archivo.nombre} - Modificado: {fecha}"
                self.lista_archivos.insert(tk.END, linea)
    
    def crear_frames(self):
        # Cargar iconos
        try:
            self.icono_abrir = ImageTk.PhotoImage(Image.open("iconos/_abrir.png").resize((25, 25)))
            self.icono_crear = ImageTk.PhotoImage(Image.open("iconos/crear.png").resize((25, 25)))
            self.icono_crear_usuario = ImageTk.PhotoImage(Image.open("iconos/crear_usuario.png").resize((25, 25)))
            self.icono_papelera = ImageTk.PhotoImage(Image.open("iconos/papelera.png").resize((25, 25)))
            self.icono_salir = ImageTk.PhotoImage(Image.open("iconos/salir.png").resize((25, 25)))
        except:
            # Si no hay iconos, usar texto solamente
            self.icono_abrir = self.icono_crear = self.icono_crear_usuario = self.icono_papelera = self.icono_salir = None

        opciones_boton = {"width": 180, "font": tema["fuente"],
                    "bg": tema["fondo_menu"], "fg": "white",
                    "activebackground": "#fc5e5b", "relief": "flat", "compound": "left"}
        
        self.menu_contextual = tk.Menu(self.root, tearoff=0, bg=tema["fondo_principal"], fg=tema["texto2"], font=tema["fuente"])
        self.menu_contextual.add_command(label="Propiedades", command=self.mostrar_propiedades_archivo)

        self.frame_superior = tk.Frame(self.root, bg=tema["seleccion"], height=10)
        self.frame_superior.pack(side=tk.TOP, fill=tk.X)

        self.frame_izquierdo = tk.Frame(self.root, bg=tema["fondo_menu"], width=250)
        self.frame_izquierdo.pack(side=tk.LEFT, fill=tk.Y)
        self.frame_izquierdo.pack_propagate(False)

        self.frame_central = tk.Frame(self.root, bg=tema["fondo_principal"])
        self.frame_central.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(self.frame_izquierdo, text="Acciones", font=(tema["fuente"][0], 14),
                 fg=tema["texto"], bg=tema["fondo_menu"]).pack(pady=15)
        
        # Botones del menú lateral
        tk.Button(self.frame_izquierdo, text="  Abrir archivo", command=self.abrir_archivo, 
                 **opciones_boton, image=self.icono_abrir).pack(pady=15)
        tk.Button(self.frame_izquierdo, text="  Crear archivo", command=self.crear_archivo, 
                 **opciones_boton, image=self.icono_crear).pack(pady=15)
        tk.Button(self.frame_izquierdo, text="  Crear usuario", command=self.crear_usuario, 
                 **opciones_boton, image=self.icono_crear_usuario).pack(pady=15)
        tk.Button(self.frame_izquierdo, text="    Papelera       ", command=self.mostrar_papelera, 
                 **opciones_boton, image=self.icono_papelera).pack(pady=15)
        tk.Button(self.frame_izquierdo, text="  Cerrar sesión", command=self.salir,
                 **opciones_boton, image=self.icono_salir).pack(pady=15)
        
        # Info del usuario actual
        tk.Label(self.frame_izquierdo, text=f"Usuario: {self.usuario_actual.nombre}",
                fg=tema["texto"], bg=tema["fondo_menu"], font=tema["fuente"]).pack(side=tk.BOTTOM, pady=10)
        tk.Label(self.frame_izquierdo, text=f"Rol: {self.usuario_actual.rol}",
                fg=tema["texto"], bg=tema["fondo_menu"], font=tema["fuente"]).pack(side=tk.BOTTOM, pady=5)

    def abrir_archivo(self):
        seleccion = self.lista_archivos.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor selecciona un archivo")
            return
        
        nombre_archivo = self.lista_archivos.get(seleccion[0]).split(" - ")[0]
        contenido = self.gestion_FAT.leer_archivo(self.usuario_actual, nombre_archivo)
        
        if contenido is not None:
            self.mostrar_editor_archivo(nombre_archivo, contenido, False)
        else:
            messagebox.showerror("Error", "No se pudo leer el archivo")

    def crear_archivo(self):
        if not self.usuario_actual.validar_permiso("escribir"):
            messagebox.showerror("Error", "No tienes permisos para crear archivos")
            return
        nombre = simpledialog.askstring("Crear archivo", "Nombre del archivo:")
        if nombre:
            if any(a.nombre == nombre and not a.estado_papelera for a in self.gestion_FAT.archivos_logicos):
                messagebox.showerror("Error", "Ya existe un archivo con ese nombre")
                return
            
            contenido = simpledialog.askstring("Contenido", "Contenido del archivo:")
            if contenido is not None:
                self.gestion_FAT.crear_archivo(self.usuario_actual, nombre, contenido)
                self.actualizar_lista_archivos()
                messagebox.showinfo("Éxito", "Archivo creado correctamente")

    def modificar_archivo(self):
        if not self.usuario_actual.validar_permiso("escribir"):
            messagebox.showerror("Error", "No tienes permisos para modificar archivos")
            return
        seleccion = self.lista_archivos.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor selecciona un archivo")
            return
        
        nombre_archivo = self.lista_archivos.get(seleccion[0]).split(" - ")[0]
        contenido_actual = self.gestion_FAT.leer_archivo(self.usuario_actual, nombre_archivo)
        
        if contenido_actual is not None:
            self.mostrar_editor_archivo(nombre_archivo, contenido_actual, True)

    def mostrar_editor_archivo(self, nombre, contenido, editable):
        # Crear ventana de edición
        editor = tk.Toplevel(self.root)
        editor.title(f"{'Editar' if editable else 'Ver'} archivo: {nombre}")
        editor.geometry("600x720")
        editor.configure(bg=tema["fondo_principal"])
        
        tk.Label(editor, text=f"Archivo: {nombre}", bg=tema["fondo_principal"], 
                fg=tema["texto2"], font=(tema["fuente"][0], 14, "bold")).pack(pady=10)
        
        # Área de texto
        frame_texto = tk.Frame(editor, bg=tema["fondo_principal"])
        frame_texto.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(frame_texto)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        texto = tk.Text(frame_texto, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                       font=tema["fuente"], bg="white", fg="black")
        texto.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=texto.yview)
        
        texto.insert("1.0", contenido)
        
        if not editable:
            texto.config(state=tk.DISABLED)
        
        # Botones
        frame_botones = tk.Frame(editor, bg=tema["fondo_principal"])
        frame_botones.pack(fill=tk.X, pady=10)
        
        if editable:
            tk.Button(frame_botones, text="Guardar", bg=tema["seleccion"], fg="white",
                     font=tema["fuente"], command=lambda: self.guardar_archivo_editado(nombre, texto.get("1.0", tk.END), editor),
                     width=15).pack(side=tk.LEFT, padx=20)
        
        tk.Button(frame_botones, text="Cerrar", bg=tema["fondo_menu"], fg="white",
                 font=tema["fuente"], command=editor.destroy,
                 width=15).pack(side=tk.RIGHT, padx=20)

    def guardar_archivo_editado(self, nombre, contenido, ventana):
        self.gestion_FAT.modificar_archivo(self.usuario_actual, nombre, contenido.strip())
        self.actualizar_lista_archivos()
        messagebox.showinfo("Éxito", "Archivo modificado correctamente")
        ventana.destroy()

    def eliminar_archivo(self):
        if not self.usuario_actual.validar_permiso("eliminar"):
            messagebox.showerror("Error", "No tienes permisos para eliminar archivos")
            return
        seleccion = self.lista_archivos.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor selecciona un archivo")
            return
        
        nombre_archivo = self.lista_archivos.get(seleccion[0]).split(" - ")[0]
        
        if messagebox.askyesno("Confirmar", f"¿Estás seguro de que quieres eliminar '{nombre_archivo}'?"):
            self.gestion_FAT.eliminar_archivo(self.usuario_actual, nombre_archivo)
            self.actualizar_lista_archivos()
            messagebox.showinfo("Éxito", "Archivo movido a la papelera")

    def crear_usuario(self):
        if not self.usuario_actual.validar_permiso("crear usuario"):
            messagebox.showerror("Error", "No tienes permisos para crear usuarios")
            return
        
        nombre = simpledialog.askstring("Crear usuario", "Nombre del usuario:")
        if nombre:
            # Recargar usuarios para verificar duplicados
            self.gestion.cargar_usuarios()
            if any(u.nombre == nombre for u in self.gestion.usuarios):
                messagebox.showerror("Error", "Ya existe un usuario con ese nombre")
                return
            
            clave = simpledialog.askstring("Contraseña", "Contraseña:", show="*")
            if clave:
                rol = simpledialog.askstring("Rol", "Rol (admin/usuario/invitado):")
                if rol in ["admin", "usuario", "invitado"]:
                    self.gestion.crear_usuario(self.usuario_actual, nombre, clave, rol)
                    messagebox.showinfo("Éxito", "Usuario creado correctamente")
                else:
                    messagebox.showerror("Error", "Rol inválido")

    def mostrar_papelera(self):
        papelera = tk.Toplevel(self.root)
        papelera.title("Papelera")
        papelera.geometry("600x720")
        papelera.configure(bg=tema["fondo_principal"])
        
        tk.Label(papelera, text="Archivos en la papelera", bg=tema["fondo_principal"], 
                fg=tema["texto2"], font=(tema["fuente"][0], 14, "bold")).pack(pady=10)
        
        # Lista de archivos en papelera
        frame_lista = tk.Frame(papelera, bg=tema["fondo_principal"])
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        lista_papelera = tk.Listbox(frame_lista, font=tema["fuente"],
                                selectbackground=tema["seleccion"],
                                bg=tema["fondo_principal"], fg="black",
                                yscrollcommand=scrollbar.set)
        lista_papelera.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=lista_papelera.yview)
        
        for archivo in self.gestion_FAT.papelera:
            # Formatear fecha para mejor visualización
            fecha = archivo.fecha_eliminacion[:16].replace('T', ' ') if archivo.fecha_eliminacion else "N/A"
            linea = f"{archivo.nombre} - Eliminado: {fecha}"
            lista_papelera.insert(tk.END, linea)
        
        # Botones
        frame_botones = tk.Frame(papelera, bg=tema["fondo_principal"])
        frame_botones.pack(fill=tk.X, pady=10)
        
        tk.Button(frame_botones, text="Recuperar seleccionado", bg=tema["seleccion"], fg="white",
                font=tema["fuente"], command=lambda: self.recuperar_archivo_papelera(lista_papelera, papelera),
                width=20).pack(side=tk.LEFT, padx=20)
        
        tk.Button(frame_botones, text="Cerrar", bg=tema["fondo_menu"], fg="white",
                font=tema["fuente"], command=papelera.destroy,
                width=15).pack(side=tk.RIGHT, padx=20)

    def recuperar_archivo_papelera(self, lista_papelera, ventana):
        seleccion = lista_papelera.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor selecciona un archivo")
            return
        
        nombre_archivo = lista_papelera.get(seleccion[0]).split(" - ")[0]
        self.gestion_FAT.recuperar_archivo(nombre_archivo)
        self.actualizar_lista_archivos()
        messagebox.showinfo("Éxito", "Archivo recuperado correctamente")
        ventana.destroy()

    def mostrar_menu_contextual(self, event):
        try:
            # Seleccionar el item bajo el cursor
            index = self.lista_archivos.nearest(event.y)
            if index >= 0:
                self.lista_archivos.selection_clear(0, tk.END)
                self.lista_archivos.selection_set(index)
                self.lista_archivos.activate(index)
                self.menu_contextual.post(event.x_root, event.y_root)
        except:
            pass

    def mostrar_propiedades_archivo(self):
        seleccion = self.lista_archivos.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor selecciona un archivo")
            return
        
        nombre_archivo = self.lista_archivos.get(seleccion[0]).split(" - ")[0]
        
        # Buscar el archivo en la lista
        archivo = None
        for a in self.gestion_FAT.archivos_logicos:
            if a.nombre == nombre_archivo and not a.estado_papelera:
                archivo = a
                break
        
        if archivo is None:
            messagebox.showerror("Error", "No se encontró el archivo")
            return
        
        # Obtener metadatos
        metadatos = archivo.mostrar_metadatos()
        
        # Crear ventana de propiedades
        self.mostrar_ventana_propiedades(metadatos)

    def mostrar_ventana_propiedades(self, metadatos):
        propiedades = tk.Toplevel(self.root)
        propiedades.title("Propiedades del archivo")
        propiedades.geometry("500x400")
        propiedades.configure(bg=tema["fondo_principal"])
        propiedades.resizable(False, False)
        
        # Título
        tk.Label(propiedades, text=f"Propiedades: {metadatos['Nombre']}", 
                bg=tema["fondo_principal"], fg=tema["texto2"], 
                font=(tema["fuente"][0], 14, "bold")).pack(pady=15)
        
        # Frame para los metadatos
        frame_metadatos = tk.Frame(propiedades, bg=tema["fondo_principal"])
        frame_metadatos.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Crear etiquetas para cada metadato
        row = 0
        for clave, valor in metadatos.items():
            # Etiqueta del campo
            lbl_clave = tk.Label(frame_metadatos, text=f"{clave}:", 
                            bg=tema["fondo_principal"], fg=tema["texto2"],
                            font=(tema["fuente"][0], 10, "bold"), anchor="w")
            lbl_clave.grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
            
            # Valor del campo
            lbl_valor = tk.Label(frame_metadatos, text=str(valor), 
                            bg=tema["fondo_principal"], fg=tema["texto2"],
                            font=tema["fuente"], anchor="w", wraplength=350)
            lbl_valor.grid(row=row, column=1, sticky="w", pady=5)
            
            row += 1
        
        # Botón cerrar
        tk.Button(propiedades, text="Cerrar", bg=tema["seleccion"], fg="white",
                font=tema["fuente"], command=propiedades.destroy,
                width=15).pack(pady=15)
        
        # Hacer que la ventana sea modal
        propiedades.transient(self.root)
        propiedades.grab_set()
        self.root.wait_window(propiedades)
    
    def mostrar_menu_contextual_papelera(self, event, lista_papelera, menu_contextual):
        try:
            index = lista_papelera.nearest(event.y)
            if index >= 0:
                lista_papelera.selection_clear(0, tk.END)
                lista_papelera.selection_set(index)
                lista_papelera.activate(index)
                menu_contextual.post(event.x_root, event.y_root)
        except:
            pass

    def mostrar_propiedades_papelera(self, lista_papelera):
        seleccion = lista_papelera.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor selecciona un archivo")
            return
        
        nombre_archivo = lista_papelera.get(seleccion[0]).split(" - ")[0]
        
        # Buscar el archivo en la papelera
        archivo = None
        for a in self.gestion_FAT.papelera:
            if a.nombre == nombre_archivo:
                archivo = a
                break
        
        if archivo is None:
            messagebox.showerror("Error", "No se encontró el archivo")
            return
        
        # Obtener metadatos
        metadatos = archivo.mostrar_metadatos()
        
        # Mostrar ventana de propiedades
        self.mostrar_ventana_propiedades(metadatos)
    
    def salir(self):
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres cerrar sesión?"):
            self.usuario_actual = None
            self.mostrar_login()



root = tk.Tk()
app = Aplicacion(root)
root.mainloop()