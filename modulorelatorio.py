# modulo7_relatorios.py
# Relatórios Gerenciais — TechVenda Ltda. (Abas 1 a 7 completas)

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import csv
import os


def conectar_db():
    """Conecta ao banco de dados techvenda_db"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",          # ALTERE SE TIVER SENHA
            database="techvenda_db",
            charset="utf8mb4"
        )
        return conn
    except Error as e:
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco:\n{e}")
        return None


class AppRelatorios:
    def __init__(self, root):
        self.root = root
        self.root.title("Relatórios Gerenciais — TechVenda")
        self.root.geometry("950x650")
        self.root.resizable(False, False)

        # Centralizar janela
        largura = 950
        altura = 650
        posx = (root.winfo_screenwidth() // 2) - (largura // 2)
        posy = (root.winfo_screenheight() // 2) - (altura // 2)
        self.root.geometry(f"{largura}x{altura}+{posx}+{posy}")

        # Notebook (Abas)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Criar todas as abas
        self.criar_aba1_resumo_geral()
        self.criar_aba2_estoque_critico()
        self.criar_aba3_melhores_clientes()
        self.criar_aba4_vendas_periodo()
        self.criar_aba5_produtos_mais_vendidos()
        self.criar_aba6_vendas_por_mes()
        self.criar_aba7_vendas_por_fornecedor()

    # ====================== ABA 1 — RESUMO GERAL ======================
    def criar_aba1_resumo_geral(self):
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text="Resumo Geral")

        frame_cards = tk.Frame(aba, padx=20, pady=20)
        frame_cards.pack(fill="both", expand=True)

        self.labels = {}

        infos = [
            ("Total de Clientes", "clientes", "#4ade80"),
            ("Total de Produtos", "produtos", "#60a5fa"),
            ("Total de Pedidos", "pedidos", "#fbbf24"),
            ("Total Faturado", "faturado", "#f87171"),
            ("Pedidos Pendentes", "pendentes", "#ff9800"),
            ("Produtos sem Estoque", "sem_estoque", "#ef4444")
        ]

        for i, (titulo, chave, cor) in enumerate(infos):
            card = tk.Frame(frame_cards, bg="#16213e", width=280, height=120, relief="raised", bd=2)
            card.grid(row=i//2, column=i%2, padx=15, pady=15, sticky="nsew")
            card.pack_propagate(False)

            tk.Label(card, text=titulo, font=("Segoe UI", 11), bg="#16213e", fg="#aaaaaa").pack(pady=8)
            self.labels[chave] = tk.Label(card, text="0", font=("Arial", 28, "bold"), bg="#16213e", fg=cor)
            self.labels[chave].pack(expand=True)

        btn_atualizar = tk.Button(aba, text="Atualizar Dados", font=("Segoe UI", 11, "bold"),
                                  bg="#22c55e", fg="white", command=self.atualizar_resumo_geral)
        btn_atualizar.pack(pady=15)

        self.atualizar_resumo_geral()

    def atualizar_resumo_geral(self):
        conn = conectar_db()
        if not conn:
            return
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM clientes")
            self.labels["clientes"].config(text=str(cursor.fetchone()[0]))

            cursor.execute("SELECT COUNT(*) FROM produtos")
            self.labels["produtos"].config(text=str(cursor.fetchone()[0]))

            cursor.execute("SELECT COUNT(*) FROM pedidos")
            self.labels["pedidos"].config(text=str(cursor.fetchone()[0]))

            cursor.execute("""
                SELECT COALESCE(SUM(p.quantidade * pr.preco), 0)
                FROM pedidos p JOIN produtos pr ON p.id_produto = pr.id_produto 
                WHERE p.status_pedido = 'Entregue'
            """)
            faturado = cursor.fetchone()[0]
            self.labels["faturado"].config(text=f"R$ {faturado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

            cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status_pedido = 'Pendente'")
            self.labels["pendentes"].config(text=str(cursor.fetchone()[0]))

            cursor.execute("SELECT COUNT(*) FROM produtos WHERE estoque = 0")
            self.labels["sem_estoque"].config(text=str(cursor.fetchone()[0]))

        except Error as e:
            messagebox.showerror("Erro", f"Erro ao atualizar resumo:\n{e}")
        finally:
            cursor.close()
            conn.close()

    # ====================== ABA 2 — ESTOQUE CRÍTICO ======================
    def criar_aba2_estoque_critico(self):
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text="Estoque Crítico")

        colunas = ("produto", "fornecedor", "preco", "estoque", "situacao")
        self.tree2 = ttk.Treeview(aba, columns=colunas, show="headings", height=18)

        self.tree2.heading("produto", text="Produto")
        self.tree2.heading("fornecedor", text="Fornecedor")
        self.tree2.heading("preco", text="Preço")
        self.tree2.heading("estoque", text="Estoque")
        self.tree2.heading("situacao", text="Situação")

        self.tree2.column("produto", width=280)
        self.tree2.column("fornecedor", width=180)
        self.tree2.column("preco", width=100, anchor="e")
        self.tree2.column("estoque", width=80, anchor="center")
        self.tree2.column("situacao", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(aba, orient="vertical", command=self.tree2.yview)
        self.tree2.configure(yscrollcommand=scrollbar.set)

        self.tree2.pack(side="left", fill="both", expand=True, padx=(10,0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        btn_frame = tk.Frame(aba)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Exportar CSV", command=lambda: self.exportar_csv(self.tree2, "Estoque_Critico")).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Atualizar", command=self.carregar_estoque_critico).pack(side="left", padx=5)

        self.carregar_estoque_critico()

    def carregar_estoque_critico(self):
        for item in self.tree2.get_children():
            self.tree2.delete(item)

        conn = conectar_db()
        if not conn: return
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT pr.nome_produto, f.nome_fornecedor, pr.preco, pr.estoque,
                CASE WHEN pr.estoque = 0 THEN 'ZERADO'
                     WHEN pr.estoque <= 5 THEN 'CRÍTICO'
                     ELSE 'BAIXO' END AS situacao
                FROM produtos pr
                LEFT JOIN fornecedor f ON pr.id_fornecedor = f.id_fornecedor
                WHERE pr.estoque <= 10
                ORDER BY pr.estoque ASC
            """)

            for row in cursor.fetchall():
                tag = row['situacao']
                valores = (
                    row['nome_produto'],
                    row['nome_fornecedor'] or "Sem fornecedor",
                    f"R$ {row['preco']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    row['estoque'],
                    row['situacao']
                )
                self.tree2.insert("", "end", values=valores, tags=(tag,))

            self.tree2.tag_configure("ZERADO", background="#ff4d4d", foreground="white")
            self.tree2.tag_configure("CRÍTICO", background="#ffaa00", foreground="black")
            self.tree2.tag_configure("BAIXO", background="#ffdd57", foreground="black")

        except Error as e:
            messagebox.showerror("Erro", str(e))
        finally:
            cursor.close()
            conn.close()

    # ====================== ABA 3 — MELHORES CLIENTES ======================
    def criar_aba3_melhores_clientes(self):
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text="Melhores Clientes")

        colunas = ("pos", "cliente", "cidade", "qtd", "total")
        self.tree3 = ttk.Treeview(aba, columns=colunas, show="headings", height=18)

        self.tree3.heading("pos", text="Posição")
        self.tree3.heading("cliente", text="Cliente")
        self.tree3.heading("cidade", text="Cidade")
        self.tree3.heading("qtd", text="Qtd Pedidos")
        self.tree3.heading("total", text="Total Gasto")

        for col in colunas:
            self.tree3.column(col, width=140, anchor="center" if col in ["pos","qtd"] else "w")

        scrollbar = ttk.Scrollbar(aba, orient="vertical", command=self.tree3.yview)
        self.tree3.configure(yscrollcommand=scrollbar.set)
        self.tree3.pack(side="left", fill="both", expand=True, padx=(10,0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        btn_frame = tk.Frame(aba)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Exportar CSV", command=lambda: self.exportar_csv(self.tree3, "Melhores_Clientes")).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Atualizar", command=self.carregar_melhores_clientes).pack(side="left", padx=5)

        self.carregar_melhores_clientes()

    def carregar_melhores_clientes(self):
        for item in self.tree3.get_children(): self.tree3.delete(item)
        conn = conectar_db()
        if not conn: return
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT c.nome, c.cidade, COUNT(p.id_pedido) AS qtd_pedidos,
                       SUM(p.quantidade * pr.preco) AS total_gasto
                FROM clientes c
                JOIN pedidos p ON c.id_cliente = p.id_cliente
                JOIN produtos pr ON p.id_produto = pr.id_produto
                GROUP BY c.id_cliente, c.nome, c.cidade
                ORDER BY total_gasto DESC LIMIT 10
            """)

            for i, row in enumerate(cursor.fetchall(), 1):
                valores = (f"{i}º", row['nome'], row['cidade'] or "-", row['qtd_pedidos'],
                           f"R$ {row['total_gasto']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                self.tree3.insert("", "end", values=valores)
        except Error as e:
            messagebox.showerror("Erro", str(e))
        finally:
            cursor.close()
            conn.close()

    # ====================== ABA 4 — VENDAS POR PERÍODO ======================
    def criar_aba4_vendas_periodo(self):
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text="Vendas por Período")

        filtro = tk.Frame(aba)
        filtro.pack(fill="x", padx=10, pady=8)

        tk.Label(filtro, text="Data Início:").pack(side="left")
        self.entry_inicio = tk.Entry(filtro, width=12)
        self.entry_inicio.pack(side="left", padx=5)
        self.entry_inicio.insert(0, datetime.now().strftime("%d/%m/%Y"))

        tk.Label(filtro, text="Data Fim:").pack(side="left", padx=(10,5))
        self.entry_fim = tk.Entry(filtro, width=12)
        self.entry_fim.pack(side="left", padx=5)
        self.entry_fim.insert(0, datetime.now().strftime("%d/%m/%Y"))

        tk.Button(filtro, text="Filtrar", command=self.carregar_vendas_periodo).pack(side="left", padx=10)

        colunas = ("id", "data", "cliente", "produto", "qtd", "total", "status")
        self.tree4 = ttk.Treeview(aba, columns=colunas, show="headings", height=15)
        # ... (configuração de headings e columns igual à versão anterior) ...
        self.tree4.heading("id", text="ID Pedido")
        self.tree4.heading("data", text="Data")
        self.tree4.heading("cliente", text="Cliente")
        self.tree4.heading("produto", text="Produto")
        self.tree4.heading("qtd", text="Qtd")
        self.tree4.heading("total", text="Total")
        self.tree4.heading("status", text="Status")

        scrollbar = ttk.Scrollbar(aba, orient="vertical", command=self.tree4.yview)
        self.tree4.configure(yscrollcommand=scrollbar.set)
        self.tree4.pack(side="left", fill="both", expand=True, padx=(10,0), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        self.label_total = tk.Label(aba, text="Total do Período: R$ 0,00", font=("Arial", 12, "bold"), fg="#00ff9d")
        self.label_total.pack(pady=8)

        btn_frame = tk.Frame(aba)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Exportar CSV", command=lambda: self.exportar_csv(self.tree4, "Vendas_Periodo")).pack(side="left", padx=5)

        self.carregar_vendas_periodo()

    def carregar_vendas_periodo(self):
        # (mesma lógica da versão anterior - limpa e carrega)
        for item in self.tree4.get_children():
            self.tree4.delete(item)

        try:
            dt_inicio = datetime.strptime(self.entry_inicio.get(), "%d/%m/%Y").strftime("%Y-%m-%d")
            dt_fim = datetime.strptime(self.entry_fim.get(), "%d/%m/%Y").strftime("%Y-%m-%d")
        except:
            messagebox.showerror("Erro", "Data inválida!")
            return

        conn = conectar_db()
        if not conn: return
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT p.id_pedido, p.data_pedido, c.nome, pr.nome_produto, p.quantidade,
                       (p.quantidade * pr.preco) AS total, p.status_pedido
                FROM pedidos p
                JOIN clientes c ON p.id_cliente = c.id_cliente
                JOIN produtos pr ON p.id_produto = pr.id_produto
                WHERE p.data_pedido BETWEEN %s AND %s
                ORDER BY p.data_pedido DESC
            """, (dt_inicio, dt_fim))

            total_geral = 0
            for row in cursor.fetchall():
                total = row['total'] or 0
                total_geral += total
                self.tree4.insert("", "end", values=(
                    row['id_pedido'],
                    row['data_pedido'].strftime("%d/%m/%Y") if hasattr(row['data_pedido'], 'strftime') else row['data_pedido'],
                    row['nome'],
                    row['nome_produto'],
                    row['quantidade'],
                    f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    row['status_pedido']
                ))
            self.label_total.config(text=f"Total do Período: R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        except Error as e:
            messagebox.showerror("Erro", str(e))
        finally:
            cursor.close()
            conn.close()

    # ====================== ABA 5 — PRODUTOS MAIS VENDIDOS ======================
    def criar_aba5_produtos_mais_vendidos(self):
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text="Produtos Mais Vendidos")

        colunas = ("pos", "produto", "fornecedor", "qtd_vendida", "total_vendido")
        self.tree5 = ttk.Treeview(aba, columns=colunas, show="headings", height=18)

        self.tree5.heading("pos", text="Posição")
        self.tree5.heading("produto", text="Produto")
        self.tree5.heading("fornecedor", text="Fornecedor")
        self.tree5.heading("qtd_vendida", text="Qtd Vendida")
        self.tree5.heading("total_vendido", text="Total (R$)")

        self.tree5.column("pos", width=70, anchor="center")
        self.tree5.column("produto", width=280)
        self.tree5.column("fornecedor", width=180)
        self.tree5.column("qtd_vendida", width=100, anchor="center")
        self.tree5.column("total_vendido", width=120, anchor="e")

        scrollbar = ttk.Scrollbar(aba, orient="vertical", command=self.tree5.yview)
        self.tree5.configure(yscrollcommand=scrollbar.set)

        self.tree5.pack(side="left", fill="both", expand=True, padx=(10,0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        btn_frame = tk.Frame(aba)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Exportar CSV", command=lambda: self.exportar_csv(self.tree5, "Produtos_Mais_Vendidos")).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Atualizar", command=self.carregar_produtos_mais_vendidos).pack(side="left", padx=5)

        self.carregar_produtos_mais_vendidos()

    def carregar_produtos_mais_vendidos(self):
        for item in self.tree5.get_children():
            self.tree5.delete(item)

        conn = conectar_db()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT 
                    pr.nome_produto, 
                    f.nome_fornecedor,
                    SUM(p.quantidade) AS qtd_vendida,
                    SUM(p.quantidade * pr.preco) AS total_vendido
                FROM pedidos p
                JOIN produtos pr ON p.id_produto = pr.id_produto
                LEFT JOIN fornecedor f ON pr.id_fornecedor = f.id_fornecedor
                WHERE p.status_pedido <> 'Cancelado'
                GROUP BY pr.id_produto, pr.nome_produto, f.nome_fornecedor
                ORDER BY qtd_vendida DESC
                LIMIT 15
            """)  # Ranking dos produtos mais vendidos (exclui cancelados)

            for i, row in enumerate(cursor.fetchall(), 1):
                total = row['total_vendido'] or 0
                valores = (
                    f"{i}º",
                    row['nome_produto'],
                    row['nome_fornecedor'] or "Sem fornecedor",
                    int(row['qtd_vendida']),
                    f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                )
                self.tree5.insert("", "end", values=valores)

        except Error as e:
            messagebox.showerror("Erro", str(e))
        finally:
            cursor.close()
            conn.close()

    # ====================== ABA 6 — VENDAS POR MÊS ======================
    def criar_aba6_vendas_por_mes(self):
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text="Vendas por Mês")

        filtro_frame = tk.Frame(aba)
        filtro_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(filtro_frame, text="Selecione o Ano:").pack(side="left", padx=5)
        self.combo_ano = ttk.Combobox(filtro_frame, width=10, state="readonly")
        self.combo_ano.pack(side="left", padx=5)

        # Anos: atual + 2 anteriores
        ano_atual = datetime.now().year
        self.combo_ano['values'] = [ano_atual, ano_atual-1, ano_atual-2]
        self.combo_ano.set(ano_atual)

        tk.Button(filtro_frame, text="Gerar Relatório", command=self.carregar_vendas_por_mes).pack(side="left", padx=15)

        # Treeview
        colunas = ("mes", "nome_mes", "total_pedidos", "total_valor")
        self.tree6 = ttk.Treeview(aba, columns=colunas, show="headings", height=18)

        self.tree6.heading("mes", text="Mês")
        self.tree6.heading("nome_mes", text="Nome do Mês")
        self.tree6.heading("total_pedidos", text="Total Pedidos")
        self.tree6.heading("total_valor", text="Total (R$)")

        self.tree6.column("mes", width=70, anchor="center")
        self.tree6.column("nome_mes", width=150)
        self.tree6.column("total_pedidos", width=120, anchor="center")
        self.tree6.column("total_valor", width=140, anchor="e")

        scrollbar = ttk.Scrollbar(aba, orient="vertical", command=self.tree6.yview)
        self.tree6.configure(yscrollcommand=scrollbar.set)

        self.tree6.pack(side="left", fill="both", expand=True, padx=(10,0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        btn_frame = tk.Frame(aba)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Exportar CSV", command=lambda: self.exportar_csv(self.tree6, "Vendas_por_Mes")).pack(side="left", padx=5)

        self.carregar_vendas_por_mes()  # Carrega inicial

    def carregar_vendas_por_mes(self):
        for item in self.tree6.get_children():
            self.tree6.delete(item)

        ano = self.combo_ano.get()
        if not ano:
            return

        conn = conectar_db()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT 
                    MONTH(p.data_pedido) AS mes,
                    COUNT(p.id_pedido) AS total_pedidos,
                    SUM(p.quantidade * pr.preco) AS total_valor
                FROM pedidos p
                JOIN produtos pr ON p.id_produto = pr.id_produto
                WHERE YEAR(p.data_pedido) = %s
                GROUP BY MONTH(p.data_pedido)
                ORDER BY mes
            """, (ano,))  # Total de vendas agrupado por mês no ano selecionado

            meses_nome = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                         "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

            for row in cursor.fetchall():
                valores = (
                    row['mes'],
                    meses_nome[row['mes']],
                    row['total_pedidos'],
                    f"R$ {row['total_valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                )
                self.tree6.insert("", "end", values=valores)

        except Error as e:
            messagebox.showerror("Erro", str(e))
        finally:
            cursor.close()
            conn.close()

    # ====================== ABA 7 — VENDAS POR FORNECEDOR ======================
    def criar_aba7_vendas_por_fornecedor(self):
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text="Vendas por Fornecedor")

        colunas = ("fornecedor", "qtd_vendida", "total_vendido", "participacao")
        self.tree7 = ttk.Treeview(aba, columns=colunas, show="headings", height=18)

        self.tree7.heading("fornecedor", text="Fornecedor")
        self.tree7.heading("qtd_vendida", text="Qtd Vendida")
        self.tree7.heading("total_vendido", text="Total Vendido (R$)")
        self.tree7.heading("participacao", text="Participação")

        self.tree7.column("fornecedor", width=280)
        self.tree7.column("qtd_vendida", width=120, anchor="center")
        self.tree7.column("total_vendido", width=160, anchor="e")
        self.tree7.column("participacao", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(aba, orient="vertical", command=self.tree7.yview)
        self.tree7.configure(yscrollcommand=scrollbar.set)

        self.tree7.pack(side="left", fill="both", expand=True, padx=(10,0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        btn_frame = tk.Frame(aba)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Exportar CSV", command=lambda: self.exportar_csv(self.tree7, "Vendas_Fornecedor")).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Atualizar", command=self.carregar_vendas_por_fornecedor).pack(side="left", padx=5)

        self.carregar_vendas_por_fornecedor()

    def carregar_vendas_por_fornecedor(self):
        for item in self.tree7.get_children():
            self.tree7.delete(item)

        conn = conectar_db()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT 
                    f.nome_fornecedor,
                    SUM(p.quantidade) AS qtd_vendida,
                    SUM(p.quantidade * pr.preco) AS total_vendido
                FROM pedidos p
                JOIN produtos pr ON p.id_produto = pr.id_produto
                LEFT JOIN fornecedor f ON pr.id_fornecedor = f.id_fornecedor
                WHERE p.status_pedido <> 'Cancelado'
                GROUP BY f.id_fornecedor, f.nome_fornecedor
                ORDER BY total_vendido DESC
            """)  # Vendas agrupadas por fornecedor

            total_geral = 0
            dados = []

            for row in cursor.fetchall():
                total = row['total_vendido'] or 0
                total_geral += total
                dados.append((row, total))

            for row, total in dados:
                participacao = f"{(total / total_geral * 100):.1f}%" if total_geral > 0 else "0%"
                valores = (
                    row['nome_fornecedor'] or "Sem fornecedor",
                    int(row['qtd_vendida']),
                    f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    participacao
                )
                self.tree7.insert("", "end", values=valores)

        except Error as e:
            messagebox.showerror("Erro", str(e))
        finally:
            cursor.close()
            conn.close()

    # ====================== FUNÇÃO EXPORTAR CSV (compartilhada) ======================
    def exportar_csv(self, treeview, nome_aba):
        if not treeview.get_children():
            messagebox.showwarning("Aviso", "Não há dados para exportar.")
            return

        try:
            pasta = "relatorios"
            if not os.path.exists(pasta):
                os.makedirs(pasta)

            data_str = datetime.now().strftime("%d%m%Y")
            nome_arquivo = f"relatorio_{nome_aba}_{data_str}.csv"
            caminho = os.path.join(pasta, nome_arquivo)

            with open(caminho, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([treeview.heading(col)["text"] for col in treeview["columns"]])
                for item in treeview.get_children():
                    writer.writerow(treeview.item(item)["values"])

            messagebox.showinfo("Sucesso", f"Relatório exportado!\nSalvo em:\n{caminho}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar:\n{e}")



# ====================== EXECUÇÃO ISOLADA ======================
if __name__ == "__main__":
    root = tk.Tk()
    app = AppRelatorios(root)
    root.mainloop()