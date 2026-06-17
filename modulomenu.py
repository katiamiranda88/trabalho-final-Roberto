# modulomenu.py
# Menu Principal Moderno — TechVenda Ltda.

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime
import importlib


def conectar_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="techvenda_db",
            charset="utf8mb4"
        )
        return conn
    except Exception as err:
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar:\n{err}")
        return None


def abrir_menu():
    root = tk.Tk()
    root.title("TechVenda — Sistema de Gestão Comercial")
    root.geometry("1150x780")
    root.resizable(False, False)
    root.configure(bg="#0f0f1a")

    # ==================== ESTILO MODERNO ====================
    style = ttk.Style()
    style.theme_use("clam")
    
    style.configure("TButton", font=("Segoe UI", 11), padding=10)
    style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))

    # ==================== HEADER ====================
    header = tk.Frame(root, bg="#1a1a2e", height=90)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(header, text="TECHVENDA", font=("Arial", 28, "bold"), 
             bg="#1a1a2e", fg="#00d4ff").pack(side="left", padx=35, pady=20)
    
    tk.Label(header, text="Sistema de Gestão Comercial", font=("Segoe UI", 13),
             bg="#1a1a2e", fg="#aaaaaa").pack(side="left", pady=25)

    tk.Label(header, text=datetime.now().strftime("%d/%m/%Y   %H:%M"), 
             bg="#1a1a2e", fg="#7777aa", font=("Segoe UI", 11)).pack(side="right", padx=35)

    # ==================== DASHBOARD ====================
    dash_frame = tk.Frame(root, bg="#0f0f1a", pady=20)
    dash_frame.pack(fill="x")

    def criar_card(titulo, valor, cor_texto="#ffffff", cor_valor="#00ff9d"):
        card = tk.Frame(dash_frame, bg="#16213e", width=240, height=140, relief="flat", bd=0)
        card.pack_propagate(False)
        card.pack(side="left", padx=18)

        tk.Label(card, text=titulo, font=("Segoe UI", 11), bg="#16213e", fg="#aaaaaa").pack(pady=(20,5))
        tk.Label(card, text=valor, font=("Arial", 32, "bold"), bg="#16213e", fg=cor_valor).pack(expand=True)
        return card

    criar_card("Total de Clientes", "0", cor_valor="#4ade80")
    criar_card("Total de Produtos", "0", cor_valor="#60a5fa")
    criar_card("Pedidos Hoje", "0", cor_valor="#fbbf24")
    criar_card("Faturamento Mês", "R$ 0,00", cor_valor="#f87171")

    # ==================== MENU DE BOTÕES ====================
    menu_frame = tk.Frame(root, bg="#0f0f1a", padx=40, pady=30)
    menu_frame.pack(fill="both", expand=True)

    botoes = [
        ("👥 Clientes", "moduloclientes", "#4ade80"),
        ("📦 Produtos", "moduloproduto", "#60a5fa"),
        ("🛒 Fornecedores", "modulo_fornecedor", "#c084fc"),
        ("💰 Registrar Venda", "modulovendas", "#f87171"),
        ("📋 Pedidos", "modulo_pedidos", "#fbbf24"),
        ("🏷️ Emitir Cupom", "modulocupom", "#67e8f9"),
        ("📊 Relatórios", "modulorelatorio", "#34d399"),
        ("📈 Relatórios Avançados", "modulo_relatorios_avancados", "#f472b6"),
        ("❌ Sair", None, "#ef4444")
    ]

    for i, (texto, modulo, cor) in enumerate(botoes):
        btn = tk.Button(
            menu_frame,
            text=texto,
            font=("Segoe UI", 12, "bold"),
            bg="#1e2937",
            fg="white",
            activebackground=cor,
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=20,
            pady=18,
            cursor="hand2",
            command=lambda m=modulo: abrir_modulo(m) if m else root.destroy()
        )
        btn.grid(row=i//3, column=i%3, padx=12, pady=12, sticky="nsew")
        
        # Efeito hover
        btn.bind("<Enter>", lambda e, b=btn, c=cor: b.config(bg=c))
        btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1e2937"))

    # Configurar grid
    for i in range(3):
        menu_frame.columnconfigure(i, weight=1)
    for i in range(3):
        menu_frame.rowconfigure(i, weight=1)

    root.mainloop()


def abrir_modulo(nomemodulo):
    if not nomemodulo:
        return
    try:
        modulo = importlib.import_module(nomemodulo)

        if hasattr(modulo, "AppClientes"):
            root = tk.Tk()
            modulo.AppClientes(root)
            root.mainloop()
        elif hasattr(modulo, "AppProdutos"):
            root = tk.Tk()
            modulo.AppProdutos(root)
            root.mainloop()
        elif hasattr(modulo, "AppFornecedores"):
            root = tk.Tk()
            modulo.AppFornecedores(root)
            root.mainloop()
        elif hasattr(modulo, "AppVendas"):
            root = tk.Tk()
            modulo.AppVendas(root)
            root.mainloop()
        elif hasattr(modulo, "AppPedidos"):
            root = tk.Tk()
            modulo.AppPedidos(root)
            root.mainloop()
        elif hasattr(modulo, "AppRelatorios"):
            root = tk.Tk()
            modulo.AppRelatorios(root)
            root.mainloop()
        elif hasattr(modulo, "abrir_menu"):
            modulo.abrir_menu()
        else:
            messagebox.showinfo("Módulo", f"{nomemodulo} carregado.")

    except ImportError:
        messagebox.showerror("Erro", f"Módulo '{nomemodulo}.py' não encontrado.")
    except Exception as e:
        messagebox.showerror("Erro ao abrir", str(e))


if __name__ == "__main__":
    abrir_menu()