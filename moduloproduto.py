# modulo_produto.py
# Gestão de Produtos — TechVenda Ltda.

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector


def conectar_db():
    try:
        conn = mysql.connector.connect(
            host="localhost", user="root", password="",
            database="techvenda_db", charset="utf8mb4"
        )
        return conn
    except Exception as err:
        messagebox.showerror("Erro de Conexão", str(err))
        return None


def voltar(janela, abrir_menu_func):
    if messagebox.askokcancel('Voltar', 'Deseja voltar ao menu principal?'):
        janela.destroy()
        abrir_menu_func()


def criar_barra_navegacao(janela, titulo, abrir_menu_func):
    frame_nav = tk.Frame(janela, bg='#1a1a2e', height=50)
    frame_nav.pack(fill='x', side='top')
    frame_nav.pack_propagate(False)
    
    tk.Button(frame_nav, text='← VOLTAR', bg='#c0392b', fg='white',
              font=('Arial', 10, 'bold'), command=lambda: voltar(janela, abrir_menu_func)
    ).pack(side='left', padx=15, pady=10)
    
    tk.Label(frame_nav, text=titulo, bg='#1a1a2e', fg='white',
             font=('Arial', 14, 'bold')).pack(side='left', padx=20)


class AppProdutos:
    def __init__(self, root):
        self.root = root
        self.root.title("Produtos — TechVenda")
        self.root.geometry("1100x680")
        self.root.resizable(False, False)
        
        criar_barra_navegacao(self.root, 'GESTÃO DE PRODUTOS', lambda: __import__("modulo_menu").abrir_menu())
        self.criar_layout()
        self.carregar_produtos()


    def criar_layout(self):
        frame_topo = ttk.Frame(self.root, padding=12)
        frame_topo.pack(fill="x")
        
        ttk.Label(frame_topo, text="PRODUTOS 📦", font=("Segoe UI", 16, "bold")).pack(side="left")
        ttk.Button(frame_topo, text="Atualizar", command=self.carregar_produtos).pack(side="right", padx=5)
        ttk.Button(frame_topo, text="Novo Produto", command=self.limpar).pack(side="right", padx=5)

        frame_main = ttk.Frame(self.root, padding=12)
        frame_main.pack(fill="both", expand=True)

        # Formulário
        frame_form = ttk.LabelFrame(frame_main, text=" Dados do Produto ", padding=15)
        frame_form.pack(side="left", fill="y", padx=(0,15))

        ttk.Label(frame_form, text="Nome:").grid(row=0, column=0, sticky="w", pady=6)
        self.entry_nome = ttk.Entry(frame_form, width=40)
        self.entry_nome.grid(row=0, column=1, pady=6)

        ttk.Label(frame_form, text="Preço (R$):").grid(row=1, column=0, sticky="w", pady=6)
        self.entry_preco = ttk.Entry(frame_form, width=20)
        self.entry_preco.grid(row=1, column=1, sticky="w", pady=6)

        ttk.Label(frame_form, text="Estoque:").grid(row=2, column=0, sticky="w", pady=6)
        self.entry_estoque = ttk.Entry(frame_form, width=20)
        self.entry_estoque.grid(row=2, column=1, sticky="w", pady=6)

        ttk.Label(frame_form, text="ID Fornecedor:").grid(row=3, column=0, sticky="w", pady=6)
        self.entry_fornecedor = ttk.Entry(frame_form, width=20)
        self.entry_fornecedor.grid(row=3, column=1, sticky="w", pady=6)

        btns = ttk.Frame(frame_form)
        btns.grid(row=4, column=0, columnspan=2, pady=15)
        ttk.Button(btns, text="SALVAR", command=self.salvar).pack(side="left", padx=5)
        ttk.Button(btns, text="ALTERAR", command=self.alterar).pack(side="left", padx=5)
        ttk.Button(btns, text="EXCLUIR", command=self.excluir).pack(side="left", padx=5)
        ttk.Button(btns, text="LIMPAR", command=self.limpar).pack(side="left", padx=5)

        # Treeview
        frame_tree = ttk.LabelFrame(frame_main, text=" Lista de Produtos ", padding=10)
        frame_tree.pack(side="right", fill="both", expand=True)

        cols = ("ID", "Produto", "Preço", "Estoque", "Fornecedor")
        self.tree = ttk.Treeview(frame_tree, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.selecionar)


    def carregar_produtos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = conectar_db()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id_produto, p.nome_produto, p.preco, p.estoque, f.nome_fornecedor 
                FROM produtos p 
                LEFT JOIN fornecedor f ON p.id_fornecedor = f.id_fornecedor 
                ORDER BY p.nome_produto
            """)
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
        finally:
            conn.close()


    def selecionar(self, event):
        sel = self.tree.selection()
        if not sel: return
        valores = self.tree.item(sel[0], "values")
        # Preencher campos (simplificado)
        self.entry_nome.delete(0, tk.END)
        self.entry_nome.insert(0, valores[1])


    def salvar(self):
        try:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO produtos (nome_produto, preco, estoque, id_fornecedor)
                VALUES (%s, %s, %s, %s)
            """, (self.entry_nome.get().strip(),
                  float(self.entry_preco.get() or 0),
                  int(self.entry_estoque.get() or 0),
                  self.entry_fornecedor.get().strip() or None))
            conn.commit()
            messagebox.showinfo("Sucesso", "Produto cadastrado!")
            self.limpar()
            self.carregar_produtos()
        except Exception as e:
            messagebox.showerror("Erro", str(e))
        finally:
            if 'conn' in locals(): conn.close()


    def limpar(self):
        self.entry_nome.delete(0, tk.END)
        self.entry_preco.delete(0, tk.END)
        self.entry_estoque.delete(0, tk.END)
        self.entry_fornecedor.delete(0, tk.END)


    def alterar(self): 
        messagebox.showinfo("Aviso", "Funcionalidade de alterar em desenvolvimento.")
    def excluir(self): 
        messagebox.showinfo("Aviso", "Funcionalidade de excluir em desenvolvimento.")


if __name__ == "__main__":
    root = tk.Tk()
    AppProdutos(root)
    root.mainloop()