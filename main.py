import tkinter as tk
from tkinter import font as tkfont
import moduloclientes 

# Funcao de abertura dos módulos 
def abrir_clientes():
    moduloclientes.abrir(root)

# Configuracao da janela principal (MENU)
root = tk.Tk()  # CORRIGIDO: de tk.TK() para tk.Tk()
root.title("TechVenda - Sistema de Gestão Comercial")
root.geometry("500x520")
root.resizable(False, False)
root.configure(bg="#1a1a2e")

# Cabecalho do sistema 
frame_header = tk.Frame(root, bg="#1a1a2e")
frame_header.pack(fill='x', pady=(30, 10))

tk.Label(frame_header, 
          text="🔹 TechVenda", bg="#1a1a2e", fg="#2196F3", font=("Arial", 28, "bold")).pack()

# CORRIGIDO: Adicionado .pack() no final da label abaixo
tk.Label(frame_header, 
         text="Sistema de Gestão Comercial", 
         bg="#1a1a2e", fg="#aaaaaa", font=("Arial", 11)).pack()

tk.Label(frame_header, 
          text="Versão 1.0", bg="#1a1a2e", fg="#555577", font=("Arial", 9)).pack(pady=(2,0))

# Separador Visual 
tk.Frame(root, bg="#2196F3", height=2).pack(fill="x", padx=40, pady=15)

# Frame do menu de módulos 
tk.Label(root, text="Selecione um Módulo", bg="#1a1a2e", fg="#cccccc", 
         font=("Arial", 11, "bold")).pack(pady=(0,12))
frame_menu = tk.Frame(root, bg="#1a1a2e")
frame_menu.pack()

btn_style = {
    "width": 28,
    "pady": 12,
    "font": ("Arial", 11, "bold"), 
    "relief": "flat", 
    "cursor": "hand2", 
    "anchor": "w",  # CORRIGIDO: de ";" para ":"
    "padx": 16
}

tk.Button(frame_menu, 
           text="🔹 Cadastro de Clientes", 
           bg="#2196F3", fg="white", command=abrir_clientes, **btn_style).pack(pady=6)

# Espaço reservado para próximos módulos
tk.Button(frame_menu,
          text="📦 Cadastro de Produtos", 
          bg="#263238", fg="#546e7a", 
          state='disabled', 
          **btn_style).pack(pady=6)

tk.Button(frame_menu,
           text="🚚 Cadastro de Fornecedores", 
           bg="#263238", fg="#546e7a", 
           state="disabled", 
           **btn_style).pack(pady=6)

tk.Button(frame_menu, 
           text="💰 Registro de Vendas",
           bg="#263238", fg="#546e7a", 
           state='disabled', 
           **btn_style).pack(pady=6)

# RODAPÉ DO SISTEMA 
tk.Frame(root, bg="#2196F3", 
          height=2).pack(fill="x", padx=40, pady=(20,8))

tk.Label(root, 
          text="Python 3 . Tkinter . SQLite3 . Material Didático", 
          bg="#1a1a2e", fg="#444466", font=("Arial", 8)).pack()

# Inicialização do Programa 
root.mainloop()  # CORRIGIDO: Adicionado os parênteses () para executar o método
