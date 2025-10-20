from funciones_FAT import Usuario, Gestion_Usuarios
import tkinter as tk
from tkinter import messagebox
import os
from PIL import Image, ImageTk

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
        self.root.title("Aplicación con Login")
        self.root.geometry("1280x720")
        self.root.configure(bg=tema["fondo_principal"])
        
        self.gestion = Gestion_Usuarios()
        self.gestion.crear_usuario("admin","2","admin")
        
        

        self.usuario_actual = None
        

        self.mostrar_login()
    
    def mostrar_login(self):

        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.login_frame = tk.Frame(self.root, bg=tema["fondo_principal"])
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(self.login_frame, text="Iniciar Sesión", bg=tema["fondo_principal"], fg=tema["texto2"], font=tema["fuente"]).pack(pady=20)
        
        tk.Label(self.login_frame, text="Nombre:", bg=tema["fondo_principal"], fg=tema["texto2"], font=tema["fuente"]).pack()
        self.entry_nombre = tk.Entry(self.login_frame, font=tema["fuente"])
        self.entry_nombre.pack(pady=5)

        tk.Label(self.login_frame, text="Clave:", bg=tema["fondo_principal"], fg=tema["texto2"], font=tema["fuente"]).pack()
        self.entry_clave = tk.Entry(self.login_frame, show="*", font=tema["fuente"])
        self.entry_clave.pack(pady=5)
        

        tk.Button(self.login_frame, text="Iniciar Sesión", bg=tema["seleccion"], fg=tema["texto"], font=tema["fuente"], command=self.intentar_login).pack(pady=20)
    
    def intentar_login(self):
        nombre = self.entry_nombre.get()
        clave = self.entry_clave.get()
        self.gestion.cargar_usuarios()

        if self.gestion.autenticar(nombre, clave):
            self.usuario_actual = next(u for u in self.gestion.usuarios if u.nombre == nombre)
            messagebox.showinfo("Éxito", f"Bienvenido, {self.usuario_actual.nombre}!")
            self.mostrar_interfaz_principal()
        else:
            messagebox.showerror("Error", "Nombre o clave incorrectos.")
    
    def mostrar_interfaz_principal(self):

        self.login_frame.destroy()
        
        self.crear_frames()

        self.mostrar_inicio()
    
    def crear_frames(self):
        self.icono_abrir = ImageTk.PhotoImage(Image.open("iconos/_abrir.png").resize((25, 25)))
        self.icono_crear = ImageTk.PhotoImage(Image.open("iconos/crear.png").resize((25, 25)))
        self.icono_crear_usuario = ImageTk.PhotoImage(Image.open("iconos\crear_usuario.png").resize((25, 25)))
        self.icono_papelera = ImageTk.PhotoImage(Image.open("iconos/papelera.png").resize((25, 25)))
        self.icono_salir = ImageTk.PhotoImage(Image.open("iconos/salir.png").resize((25, 25)))


        opciones_boton = {"width": 180, "font": tema["fuente"],
                    "bg": tema["fondo_menu"], "fg": "white",
                    "activebackground": "#fc5e5b", "relief": "flat", "compound": "left"}


        self.frame_superior = tk.Frame(self.root, bg=tema["seleccion"], height=10)
        self.frame_superior.pack(side=tk.TOP, fill=tk.X)

        self.frame_izquierdo = tk.Frame(self.root, bg=tema["fondo_menu"], width=250)
        self.frame_izquierdo.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(self.frame_izquierdo, text="Acciones", font=(tema["fuente"][0], 14, 'bold'),
                 fg=tema["texto"], bg=tema["fondo_menu"]).pack(pady=5)
        

        tk.Button(self.frame_izquierdo, text="  Abrir archivo ", command=self.mostrar_config, **opciones_boton, image=self.icono_abrir).pack(pady=25)
        tk.Button(self.frame_izquierdo, text="  Crear archivo", command=self.mostrar_config, **opciones_boton, image=self.icono_crear).pack(pady=25)
        tk.Button(self.frame_izquierdo, text="  Crear usuario", command=self.mostrar_config, **opciones_boton, image=self.icono_crear_usuario).pack(pady=25)
        tk.Button(self.frame_izquierdo, text="    Papelera       ", command=self.mostrar_config, **opciones_boton, image=self.icono_papelera).pack(pady=25)
        tk.Button(self.frame_izquierdo, text="  Cerrar sesión  ", command=self.salir,**opciones_boton, image=self.icono_salir).pack(pady=25)

        self.frame_central = tk.Frame(self.root, bg=tema["fondo_principal"])
        self.frame_central.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    def mostrar_inicio(self):
        for widget in self.frame_central.winfo_children():
            widget.destroy()
        
        tk.Label(self.frame_central, text=f"Lista de archivos:", bg=tema["fondo_principal"], fg=tema["texto2"], font=tema["fuente"]).pack(expand=True)
    
    def mostrar_config(self):
        for widget in self.frame_central.winfo_children():
            widget.destroy()
        
        tk.Label(self.frame_central, text="Configuración", bg=tema["fondo_principal"], fg=tema["texto2"], font=tema["fuente"]).pack(expand=True)
    
    def salir(self):
        self.usuario_actual = None
        self.mostrar_login()


root = tk.Tk()
app = Aplicacion(root)
root.mainloop()

