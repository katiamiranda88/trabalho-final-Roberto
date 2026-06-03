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
tk.label(frame_header,
         text="Versão 1.0",
         bg="#1a1a2e", fg="#555577",
         font=("Arial", 9)).pack(pady=2, 0)

#SEPARADOR VISUAL

tk.Frame(root, bg="#2196f3"
Cria uma linha horizontal azul como separador visual
    height==2).pack(fill="x", padx=40, pady=15))

#FRAME DO MENU DE MÓDULOS

tk.Label(root,
         text="Selecione um módulo",
         bg="#1a1a2e", fg=#"cccccc",
         font=("Arial", 11, "bold")).pack(pady=0, 12))

frame_menu = tk.Frame(root, bg="#1a1a2e")

frame_menu.pack()

btn_style = {
    "width": 28,
    "pady": 12,
    "font": ("Arial", 11, "bold"),
    "relief": "flat"
    "cursor": "hand2",
    "anchor": "w",
    "padx": 16
}

tk.Button(frame_menu,
          text="? Cadastro de Clientes",
          bg="#2196F3", fg="white",
          command=abrir_clientes,
          **btn_style).pack(pady=6))

#----ESPAÇO RESERVADO PARA OS PRÓXIMOS MÓDULO----

tk.Button(frame_menu,
          text="? Cadastro de Produtos",
          bg="#263238", fg"546e7a",
          state="disabled",
          **btn_style).pack(pady=6))

tk.Button(frame_menu,
          text="? Cadastro de Fornecedores",
          bg="#263238", fg"546e7a",
          state="disabled",
          **btn_style).pack(pady=6))

#CÓDIGO PYTHON
tk.Button(frame_menu,
          text=" Registro de Vendas",
          bg="263238", fg="#546e7a",
          state="disabled",
          **btn_style).pack(pady=6)

#RODAPÉ DO SISTEMA

tk.Frame(root, bg="#2196F3",
         
     height=2).pack(fill="x", padx=40, pady=(20, 8))
tk.Label(root,
         
         text="Python 3 . Tkinter . SQLite3 . 
Material Didático",
    
    bg="#1a1a2e", fg="#444466",
    font=("Arial", 8)).pack()

#INICIALIZAÇÃO DO SISTEMA

root.mainloop()


