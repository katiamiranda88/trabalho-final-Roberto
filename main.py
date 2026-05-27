import tkinter as tk
from tkinter import font as tkfont
import modulo_clientes

#FUNÇÕES DE ABERTURA DOS MÓDULOS

def abrir_clientes():
    modulo_clientes.abrir(root)
    
#CONFIGURACAO DA JANELA PRINCIPAL(MENU)

root = tk.tk()
root.title("TechVenda - Sistema de Gestão Comercial")
root.geometry("500x520")
root.resizable(False, False)
root.confifgure(bg="#1a1a2e")
#Define a cor de fundo azul escuro

#CABECALHO DO SISTEMA

frame_header = tk.Frame(root, bg="1a1a2e")
#Cria o frame do cabeçalho

frame_header.pack(fill="x", pady=(30, 10))

tk.Label(frame_header,
         text="? TechVenda",
         bg="#1a1a2e", fg="#2196F3"
         font=("Arial", 28, "bold")).pack()

tk.Label(frame_header,
         text="Sistema de Gestão Comercial",
         bg="#1a1a2e", fg="#aaaaaa",
         font=("Arial", 11)).pack()




