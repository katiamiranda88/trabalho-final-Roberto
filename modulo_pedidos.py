# modulo_pedidos.py
# Tela aprimorada de consulta e gestão de pedidos — TechVenda

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime


# ==================== FUNÇÕES DE NAVEGAÇÃO ====================
def voltar(janela, abrir_menu_func):
    """Fecha a janela atual e reabre o menu principal"""
    resposta = messagebox.askokcancel(
        'Voltar ao Menu',
        'Deseja voltar ao menu principal?\nDados não salvos serão perdidos.'
    )
    if resposta:
        janela.destroy()
        abrir_menu_func()


def criar_barra_navegacao(janela, titulo_tela, abrir_menu_func):
    """Cria uma barra de navegação no topo da janela"""
    # Frame da barra de navegação no topo
    frame_nav = tk.Frame(janela, bg='#1a1a2e', height=45)
    frame_nav.pack(fill='x', side='top')
    frame_nav.pack_propagate(False)
    
    # Botão VOLTAR
    btn_voltar = tk.Button(
        frame_nav,
        text='← VOLTAR',
        bg='#c0392b',
        fg='white',
        font=('Arial', 10, 'bold'),
        cursor='hand2',
        relief='flat',
        padx=12, pady=6,
        command=lambda: voltar(janela, abrir_menu_func)
    )
    btn_voltar.pack(side='left', padx=10, pady=6)
    
    # Título da tela
    lbl_titulo = tk.Label(
        frame_nav,
        text=titulo_tela,
        bg='#1a1a2e',
        fg='white',
        font=('Arial', 13, 'bold')
    )
    lbl_titulo.pack(side='left', padx=20)
    
    # Nome do sistema
    lbl_sistema = tk.Label(
        frame_nav,
        text='TechVenda Ltda.',
        bg='#1a1a2e',
        fg='#aaaaaa',
        font=('Arial', 9)
    )
    lbl_sistema.pack(side='right', padx=15)
    
    return frame_nav


def abrir_menu_principal():
    """Reabre o menu principal"""
    try:
        import modulomenu
        modulomenu.abrir_menu()
    except ImportError:
        messagebox.showinfo('Aviso', 'Módulo do menu principal não encontrado.')


# ==================== CONEXÃO COM O BANCO ====================
def conectar_db():
    """Retorna conexão com o banco techvenda_db"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="techvenda_db"
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco:\n{err}")
        return None


# ==================== JANELA PRINCIPAL ====================
class AppPedidos:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestão de Pedidos — TechVenda")
        self.root.geometry("1000x620")
        self.root.resizable(False, False)
        
        # Barra de Navegação
        criar_barra_navegacao(self.root, 'GESTÃO DE PEDIDOS', abrir_menu_principal)
        
        # Atalho de teclado
        self.root.bind('<Alt-Left>', lambda e: voltar(self.root, abrir_menu_principal))
        
        # Variáveis
        self.pedido_id_selecionado = None
        self.produto_id_selecionado = None
        self.quantidade_selecionada = 0
        
        self.var_status = tk.StringVar(value="Todos")
        self.var_data_inicio = tk.StringVar()
        self.var_data_fim = tk.StringVar()
        self.var_cliente = tk.StringVar()
        
        # Estilo
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.criar_layout()


    def criar_layout(self):
        """Cria o layout em 3 regiões"""
        
        # ==================== REGIÃO TOPO - FILTROS ====================
        frame_topo = ttk.Frame(self.root, padding=10)
        frame_topo.pack(fill="x")
        
        ttk.Label(frame_topo, text="Status:").pack(side="left", padx=(0, 5))
        self.combo_status = ttk.Combobox(frame_topo, textvariable=self.var_status, 
                                       values=["Todos", "Pendente", "Em Andamento", "Entregue", "Cancelado"], 
                                       state="readonly", width=15)
        self.combo_status.pack(side="left", padx=(0, 15))
        
        ttk.Label(frame_topo, text="Data Início:").pack(side="left", padx=(0, 5))
        self.entry_data_ini = ttk.Entry(frame_topo, textvariable=self.var_data_inicio, width=12)
        self.entry_data_ini.pack(side="left", padx=(0, 15))
        
        ttk.Label(frame_topo, text="Data Fim:").pack(side="left", padx=(0, 5))
        self.entry_data_fim = ttk.Entry(frame_topo, textvariable=self.var_data_fim, width=12)
        self.entry_data_fim.pack(side="left", padx=(0, 15))
        
        ttk.Label(frame_topo, text="Cliente:").pack(side="left", padx=(0, 5))
        self.entry_cliente = ttk.Entry(frame_topo, textvariable=self.var_cliente, width=25)
        self.entry_cliente.pack(side="left", padx=(0, 15))
        
        ttk.Button(frame_topo, text="Filtrar", command=self.carregar_pedidos).pack(side="left", padx=5)
        ttk.Button(frame_topo, text="Limpar Filtros", command=self.limpar_filtros).pack(side="left", padx=5)
        
        # ==================== REGIÃO MEIO - TREEVIEW ====================
        frame_meio = ttk.Frame(self.root, padding=10)
        frame_meio.pack(fill="both", expand=True)
        
        colunas = ("id_pedidos", "Data", "Cliente", "Produto", "Qtd", "Total", "Status")
        self.tree = ttk.Treeview(frame_meio, columns=colunas, show="headings", height=15)
        
        for col in colunas:
            self.tree.heading(col, text=col)
        
        self.tree.column("id_pedidos", width=60, anchor="center")
        self.tree.column("Data", width=110)
        self.tree.column("Cliente", width=180)
        self.tree.column("Produto", width=200)
        self.tree.column("Qtd", width=60, anchor="center")
        self.tree.column("Total", width=100, anchor="e")
        self.tree.column("Status", width=110, anchor="center")
        
        scrollbar = ttk.Scrollbar(frame_meio, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.tag_configure("Pendente", background="#fff3cd")
        self.tree.tag_configure("Entregue", background="#d4edda")
        self.tree.tag_configure("Cancelado", background="#f8d7da")
        
        self.tree.bind("<<TreeviewSelect>>", self.selecionar_pedido)
        
        # ==================== REGIÃO RODAPÉ - DETALHES ====================
        frame_rodape = ttk.LabelFrame(self.root, text="Detalhes do Pedido Selecionado", padding=15)
        frame_rodape.pack(fill="x", padx=10, pady=8)
        
        self.lbl_info = ttk.Label(frame_rodape, text="Selecione um pedido na tabela acima para ver detalhes.", 
                                foreground="gray")
        self.lbl_info.pack(anchor="w", pady=5)
        
        frame_acoes = ttk.Frame(frame_rodape)
        frame_acoes.pack(fill="x", pady=8)
        
        ttk.Label(frame_acoes, text="Alterar Status:").pack(side="left", padx=(0, 5))
        self.combo_novo_status = ttk.Combobox(frame_acoes, values=["Pendente", "Em Andamento", "Entregue", "Cancelado"], 
                                            state="readonly", width=18)
        self.combo_novo_status.pack(side="left", padx=(0, 10))
        
        ttk.Button(frame_acoes, text="CONFIRMAR ALTERAÇÃO", command=self.alterar_status).pack(side="left", padx=5)
        ttk.Button(frame_acoes, text="VER CUPOM", command=self.ver_cupom).pack(side="left", padx=5)
        ttk.Button(frame_acoes, text="EXCLUIR PEDIDO", command=self.excluir_pedido).pack(side="left", padx=5)
        
        self.lbl_totais = ttk.Label(frame_rodape, text="Total de pedidos filtrados: 0 | Valor total: R$ 0,00", 
                                  font=("Segoe UI", 10, "bold"))
        self.lbl_totais.pack(anchor="e", pady=5)
        
        self.carregar_pedidos()


    def limpar_filtros(self):
        self.var_status.set("Todos")
        self.var_data_inicio.set("")
        self.var_data_fim.set("")
        self.var_cliente.set("")
        self.carregar_pedidos()


    def carregar_pedidos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        conn = conectar_db()
        if not conn: return
        try:
            cursor = conn.cursor()
            sql = """
                SELECT p.id_pedido, p.data_pedido, c.nome AS cliente, 
                       pr.nome_produto, p.quantidade, 
                       (p.quantidade * pr.preco) AS total,
                       p.status_pedido
                FROM pedidos p
                JOIN clientes c ON p.id_cliente = c.id_cliente
                JOIN produtos pr ON p.id_produto = pr.id_produto
                WHERE 1=1
            """
            params = []
            
            if self.var_status.get() != "Todos":
                sql += " AND p.status_pedido = %s"
                params.append(self.var_status.get())
            
            data_ini = self.var_data_inicio.get().strip()
            data_fim = self.var_data_fim.get().strip()
            if data_ini and data_fim:
                try:
                    d_ini = datetime.strptime(data_ini, "%d/%m/%Y").strftime("%Y-%m-%d")
                    d_fim = datetime.strptime(data_fim, "%d/%m/%Y").strftime("%Y-%m-%d")
                    sql += " AND p.data_pedido BETWEEN %s AND %s"
                    params.extend([d_ini, d_fim])
                except:
                    pass
            
            cliente = self.var_cliente.get().strip()
            if cliente:
                sql += " AND c.nome LIKE %s"
                params.append(f"%{cliente}%")
            
            sql += " ORDER BY p.id_pedido DESC"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            total_pedidos = 0
            valor_total = 0.0
            for row in rows:
                id_ped, data, cliente, produto, qtd, total, status = row
                data_fmt = data.strftime("%d/%m/%Y %H:%M") if isinstance(data, datetime) else str(data)
                
                tag = status if status in ["Pendente", "Entregue", "Cancelado"] else "Em Andamento"
                
                self.tree.insert("", "end", values=(
                    id_ped, data_fmt, cliente, produto, qtd, f"{total:.2f}", status
                ), tags=(tag,))
                
                total_pedidos += 1
                valor_total += float(total or 0)
            
            self.lbl_totais.config(
                text=f"Total de pedidos filtrados: {total_pedidos} | Valor total: R$ {valor_total:,.2f}"
            )
        finally:
            conn.close()


    def selecionar_pedido(self, event):
        selecao = self.tree.selection()
        if not selecao: return
        valores = self.tree.item(selecao[0], "values")
        self.pedido_id_selecionado = valores[0]
        
        conn = conectar_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id_produto, quantidade FROM pedidos WHERE id_pedido = %s", 
                             (self.pedido_id_selecionado,))
                dados = cursor.fetchone()
                if dados:
                    self.produto_id_selecionado = dados[0]
                    self.quantidade_selecionada = dados[1]
            finally:
                conn.close()
        
        info_text = f"Pedido ID: {valores[0]}   |   Data: {valores[1]}\nCliente: {valores[2]}\nProduto: {valores[3]}   |   Qtd: {valores[4]}   |   Total: R$ {valores[5]}"
        self.lbl_info.config(text=info_text, foreground="black")


    def alterar_status(self):
        if not self.pedido_id_selecionado:
            messagebox.showwarning("Atenção", "Selecione um pedido.")
            return
        novo_status = self.combo_novo_status.get()
        if not novo_status:
            messagebox.showwarning("Atenção", "Selecione o novo status.")
            return
        
        conn = conectar_db()
        if not conn: return
        try:
            cursor = conn.cursor()
            if novo_status == "Cancelado":
                cursor.execute("UPDATE produtos SET estoque = estoque + %s WHERE id_produto = %s",
                             (self.quantidade_selecionada, self.produto_id_selecionado))
            
            cursor.execute("UPDATE pedidos SET status_pedido = %s WHERE id_pedido = %s",
                         (novo_status, self.pedido_id_selecionado))
            conn.commit()
            messagebox.showinfo("Sucesso", f"Status alterado para '{novo_status}'!")
            self.carregar_pedidos()
        finally:
            conn.close()


    def ver_cupom(self):
        if not self.pedido_id_selecionado:
            messagebox.showwarning("Atenção", "Selecione um pedido.")
            return
        messagebox.showinfo("Cupom", f"Exibindo cupom do pedido #{self.pedido_id_selecionado}")


    def excluir_pedido(self):
        if not self.pedido_id_selecionado:
            messagebox.showwarning("Atenção", "Selecione um pedido.")
            return
        if messagebox.askyesno("Confirmação", "Excluir este pedido?"):
            conn = conectar_db()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM pedidos WHERE id_pedido = %s", (self.pedido_id_selecionado,))
                    conn.commit()
                    messagebox.showinfo("Sucesso", "Pedido excluído!")
                    self.carregar_pedidos()
                finally:
                    conn.close()


# ==================== EXECUÇÃO ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = AppPedidos(root)
    root.mainloop()