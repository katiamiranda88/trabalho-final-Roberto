# modulo5_vendas.py
# Registrar Venda — TechVenda Ltda.

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime


# ==================== FUNÇÕES DE NAVEGAÇÃO ====================
def voltar(janela, voltar_callback=None):
    """Volta ao menu principal de forma segura"""
    if messagebox.askokcancel('Voltar ao Menu', 
                             'Deseja voltar ao menu principal?\nDados não salvos serão perdidos.'):
        janela.destroy()
        if voltar_callback:
            try:
                voltar_callback()
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível voltar ao menu.\n\n{e}")
        else:
            messagebox.showerror("Erro", "Não foi possível voltar ao menu (callback não fornecido).")


def criar_barra_navegacao(janela, titulo_tela, abrir_menu_func):
    frame_nav = tk.Frame(janela, bg='#1a1a2e', height=45)
    frame_nav.pack(fill='x', side='top')
    frame_nav.pack_propagate(False)
    
    tk.Button(
        frame_nav, text='← VOLTAR', bg='#c0392b', fg='white',
        font=('Arial', 10, 'bold'), cursor='hand2', relief='flat',
        padx=12, pady=6, command=lambda: voltar(janela, abrir_menu_func)
    ).pack(side='left', padx=10, pady=6)
    
    tk.Label(
        frame_nav, text=titulo_tela, bg='#1a1a2e', fg='white',
        font=('Arial', 13, 'bold')
    ).pack(side='left', padx=20)
    
    tk.Label(
        frame_nav, text='TechVenda Ltda.', bg='#1a1a2e', fg='#aaaaaa',
        font=('Arial', 9)
    ).pack(side='right', padx=15)


def abrir_menu_principal():
    try:
        import modulomenu
        modulomenu.abrir_menu()
    except ImportError:
        messagebox.showinfo('Aviso', 'Módulo do menu principal não encontrado.')


# ==================== CONEXÃO COM O BANCO ====================
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
    except mysql.connector.Error as err:
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco:\n{err}")
        return None


# ==================== JANELA PRINCIPAL ====================
class AppVendas:
    def __init__(self, root):
        self.root = root
        self.root.title("Registrar Venda — TechVenda")
        self.root.geometry("1080x700")
        self.root.resizable(False, False)
        
        criar_barra_navegacao(self.root, 'REGISTRAR VENDA', abrir_menu_principal)
        self.root.bind('<Alt-Left>', lambda e: voltar(self.root, abrir_menu_principal))
        
        self.venda_itens = []  # [(id_produto, quantidade, preco), ...]
        self.criar_layout()


    def criar_layout(self):
        # ==================== DADOS DO CLIENTE ====================
        frame_cliente = ttk.LabelFrame(self.root, text="Dados do Cliente", padding=10)
        frame_cliente.pack(fill="x", padx=15, pady=8)
        
        ttk.Label(frame_cliente, text="Cliente:").grid(row=0, column=0, sticky="w", padx=(0,5))
        self.combo_cliente = ttk.Combobox(frame_cliente, width=60, state="readonly")
        self.combo_cliente.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(frame_cliente, text="Buscar Cliente", command=self.buscar_cliente).grid(row=0, column=2, padx=5)

        # ==================== ADICIONAR PRODUTO ====================
        frame_produto = ttk.LabelFrame(self.root, text="Adicionar Produto", padding=10)
        frame_produto.pack(fill="x", padx=15, pady=8)
        
        ttk.Label(frame_produto, text="Produto:").grid(row=0, column=0, sticky="w", padx=(0,5))
        self.combo_produto = ttk.Combobox(frame_produto, width=45, state="readonly")
        self.combo_produto.grid(row=0, column=1, padx=5)
        
        ttk.Label(frame_produto, text="Qtd:").grid(row=0, column=2, sticky="w", padx=(15,5))
        self.entry_qtd = ttk.Entry(frame_produto, width=10)
        self.entry_qtd.grid(row=0, column=3, padx=5)
        
        ttk.Button(frame_produto, text="Adicionar Item", command=self.adicionar_item).grid(row=0, column=4, padx=10)

        # ==================== ITENS DA VENDA ====================
        frame_itens = ttk.LabelFrame(self.root, text="Itens da Venda", padding=10)
        frame_itens.pack(fill="both", expand=True, padx=15, pady=8)
        
        colunas = ("Produto", "Qtd", "Preço Unit.", "Total Item")
        self.tree_venda = ttk.Treeview(frame_itens, columns=colunas, show="headings", height=12)
        for col in colunas:
            self.tree_venda.heading(col, text=col)
            self.tree_venda.column(col, width=190, anchor='center')
        self.tree_venda.pack(fill="both", expand=True)

        # ==================== RODAPÉ ====================
        frame_rodape = ttk.Frame(self.root, padding=15)
        frame_rodape.pack(fill="x")
        
        self.lbl_total = ttk.Label(frame_rodape, text="Total da Venda: R$ 0,00", 
                                 font=("Segoe UI", 16, "bold"), foreground="#2e7d32")
        self.lbl_total.pack(side="left")
        
        ttk.Button(frame_rodape, text="Limpar Venda", command=self.limpar_venda).pack(side="right", padx=5)
        ttk.Button(frame_rodape, text="Finalizar Venda", command=self.finalizar_venda).pack(side="right", padx=5)
        
        self.carregar_combos()


    def carregar_combos(self):
        conn = conectar_db()
        if not conn: return
        try:
            cursor = conn.cursor(dictionary=True)

            # Clientes
            cursor.execute("SELECT id_cliente, nome FROM clientes ORDER BY nome")
            clientes = cursor.fetchall()
            self.combo_cliente['values'] = [f"{row['nome']} (ID: {row['id_cliente']})" for row in clientes]

            # Produtos
            cursor.execute("SELECT id_produto, nome_produto, preco FROM produtos ORDER BY nome_produto")
            produtos = cursor.fetchall()
            self.produtos_map = {p['nome_produto']: (p['id_produto'], float(p['preco'])) for p in produtos}
            self.combo_produto['values'] = list(self.produtos_map.keys())

        except Exception as e:
            messagebox.showerror("Erro ao carregar dados", str(e))
        finally:
            conn.close()


    def adicionar_item(self):
        produto_nome = self.combo_produto.get()
        qtd_str = self.entry_qtd.get().strip()

        if not produto_nome or not qtd_str:
            messagebox.showwarning("Atenção", "Selecione um produto e informe a quantidade.")
            return

        try:
            qtd = int(qtd_str)
            if qtd <= 0:
                raise ValueError("Quantidade deve ser maior que zero")
        except:
            messagebox.showerror("Erro", "Quantidade inválida.")
            return

        if produto_nome not in self.produtos_map:
            messagebox.showerror("Erro", "Produto não encontrado.")
            return

        id_prod, preco = self.produtos_map[produto_nome]
        total_item = preco * qtd

        self.tree_venda.insert("", "end", values=(
            produto_nome, 
            qtd, 
            f"R$ {preco:,.2f}", 
            f"R$ {total_item:,.2f}"
        ))
        
        self.venda_itens.append((id_prod, qtd, preco))
        self.atualizar_total()


    def atualizar_total(self):
        total = sum(qtd * preco for _, qtd, preco in self.venda_itens)
        self.lbl_total.config(text=f"Total da Venda: R$ {total:,.2f}")


    def finalizar_venda(self):
        if not self.venda_itens:
            messagebox.showwarning("Atenção", "Adicione pelo menos um produto.")
            return

        cliente_texto = self.combo_cliente.get()
        if not cliente_texto:
            messagebox.showwarning("Atenção", "Selecione um cliente.")
            return

        try:
            id_cliente = int(cliente_texto.split("(ID:")[-1].strip(" )"))
        except:
            messagebox.showerror("Erro", "Não foi possível ler o ID do cliente.")
            return

        conn = conectar_db()
        if not conn: return

        try:
            cursor = conn.cursor()
            
            for id_produto, quantidade, preco in self.venda_itens:
                cursor.execute("""
                    INSERT INTO pedidos 
                    (id_cliente, id_produto, quantidade, data_pedido, status_pedido)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_cliente, id_produto, quantidade, datetime.now().date(), "Finalizado"))

            conn.commit()
            
            total = sum(qtd * preco for _, qtd, preco in self.venda_itens)
            messagebox.showinfo("Sucesso", 
                              f"Venda registrada com sucesso!\n"
                              f"Itens: {len(self.venda_itens)}\n"
                              f"Total: R$ {total:,.2f}")
            
            self.limpar_venda()

        except mysql.connector.Error as err:
            conn.rollback()
            messagebox.showerror("Erro no Banco", f"Erro ao salvar venda:\n{err}")
        finally:
            conn.close()


    def limpar_venda(self):
        for item in self.tree_venda.get_children():
            self.tree_venda.delete(item)
        self.venda_itens.clear()
        self.lbl_total.config(text="Total da Venda: R$ 0,00")


    def buscar_cliente(self):
        messagebox.showinfo("Buscar Cliente", "Funcionalidade em desenvolvimento.")


# ==================== EXECUÇÃO ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = AppVendas(root)
    root.mainloop()