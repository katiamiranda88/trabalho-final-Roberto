# modulocupom.py
# Emitir Cupom Fiscal — TechVenda Ltda.
# Integrado com o menu principal

import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import os


def conectar_db():
    """Função de conexão reutilizável com o banco"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",          # ALTERE SE TIVER SENHA
            database="techvenda_db",
            charset="utf8mb4"
        )
        return conn
    except Exception as err:
        messagebox.showerror("Erro de Banco", f"Não foi possível conectar:\n{err}")
        return None


def buscar_dados_pedido(id_pedido):
    """
    Busca dados do pedido para gerar o cupom.
    """
    conn = conectar_db()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                p.id_pedido, 
                p.data_pedido, 
                p.quantidade,
                p.status_pedido,
                c.nome AS nome_cliente,
                pr.nome_produto, 
                pr.preco,
                (p.quantidade * pr.preco) AS total
            FROM pedidos p
            JOIN clientes c ON p.id_cliente = c.id_cliente
            JOIN produtos pr ON p.id_produto = pr.id_produto
            WHERE p.id_pedido = %s
        """
        cursor.execute(query, (id_pedido,))
        dados = cursor.fetchone()
        return dados
    except Error as e:
        messagebox.showerror("Erro", f"Erro ao buscar pedido:\n{e}")
        return None
    finally:
        if conn:
            conn.close()


def montar_cupom(dados):
    """
    Monta o cupom formatado com largura de 48 caracteres.
    """
    if not dados:
        return "ERRO: Dados do pedido não encontrados."

    # Formatação de data
    data_pedido = dados['data_pedido']
    if isinstance(data_pedido, datetime):
        data_str = data_pedido.strftime("%d/%m/%Y %H:%M")
        data_emit = data_pedido.strftime("%d/%m/%Y")
        hora_emit = data_pedido.strftime("%H:%M:%S")
    else:
        try:
            dt = datetime.strptime(str(data_pedido)[:19], "%Y-%m-%d %H:%M:%S")
            data_str = dt.strftime("%d/%m/%Y %H:%M")
            data_emit = dt.strftime("%d/%m/%Y")
            hora_emit = dt.strftime("%H:%M:%S")
        except:
            agora = datetime.now()
            data_str = agora.strftime("%d/%m/%Y %H:%M")
            data_emit = agora.strftime("%d/%m/%Y")
            hora_emit = agora.strftime("%H:%M:%S")

    cupom = "=" * 48 + "\n"
    cupom += "TECHVENDA LTDA.\n".center(48)
    cupom += "Dist. de Informatica — CNPJ: 00.000/0001-00\n".center(48)
    cupom += "=" * 48 + "\n\n"

    cupom += f"PEDIDO Nº: {dados['id_pedido']:04d}   DATA: {data_str}\n"
    cupom += f"CLIENTE: {dados['nome_cliente']}\n"
    cupom += "-" * 48 + "\n"

    # Cabeçalho da tabela
    cupom += "PRODUTO".ljust(28) + "QTD".center(6) + "UNIT".rjust(9) + " TOTAL\n"
    cupom += "-" * 48 + "\n"

    # Item
    nome_prod = str(dados['nome_produto'])[:25]
    qtd = str(dados['quantidade']).rjust(4)
    unit = f"R${dados['preco']:,.2f}".replace(",", ".").rjust(10)
    total = f"R${dados['total']:,.2f}".replace(",", ".").rjust(10)

    cupom += nome_prod.ljust(28) + qtd + unit + total + "\n\n"
    cupom += "-" * 48 + "\n"
    cupom += f"TOTAL GERAL: {f'R${dados['total']:,.2f}'.replace(',', '.').rjust(36)}\n"
    cupom += "=" * 48 + "\n"

    cupom += f"Status: {dados.get('status_pedido', 'Pendente')}\n"
    cupom += "Obrigado pela preferencia! Volte sempre.\n"
    cupom += f"Emitido em: {data_emit} as {hora_emit}\n"
    cupom += "=" * 48 + "\n"

    return cupom


def salvar_cupom(id_pedido):
    """Salva o cupom em arquivo .txt"""
    dados = buscar_dados_pedido(id_pedido)
    if not dados:
        return None

    texto = montar_cupom(dados)

    pasta = "cupons"
    if not os.path.exists(pasta):
        os.makedirs(pasta)

    agora = datetime.now()
    nome = f"cupom_{id_pedido:04d}_{agora.strftime('%Y%m%d_%H%M%S')}.txt"
    caminho = os.path.join(pasta, nome)

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)

    return caminho


def exibir_cupom(id_pedido):
    """Abre janela com o cupom"""
    dados = buscar_dados_pedido(id_pedido)
    if not dados:
        return

    texto = montar_cupom(dados)

    janela = tk.Toplevel()
    janela.title(f"Cupom - Pedido {id_pedido:04d}")
    janela.geometry("620x520")
    janela.configure(bg="#0f0f1a")

    text_widget = tk.Text(janela, font=("Courier", 11), bg="#1a1a2e", fg="#e0e0e0", wrap=tk.NONE)
    text_widget.insert("1.0", texto)
    text_widget.config(state="disabled")

    scrollbar = ttk.Scrollbar(janela, orient="vertical", command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)

    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Botões
    btn_frame = tk.Frame(janela, bg="#0f0f1a")
    btn_frame.pack(pady=8)

    tk.Button(btn_frame, text="Salvar .txt", bg="#22c55e", fg="white", font=("Segoe UI", 10, "bold"),
              command=lambda: salvar_e_notificar(id_pedido)).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Fechar", bg="#ef4444", fg="white", font=("Segoe UI", 10, "bold"),
              command=janela.destroy).pack(side=tk.LEFT, padx=10)


def salvar_e_notificar(id_pedido):
    caminho = salvar_cupom(id_pedido)
    if caminho:
        messagebox.showinfo("Sucesso", f"Cupom salvo com sucesso!\n{caminho}")


def abrir_menu():
    """Função chamada pelo menu principal"""
    root = tk.Tk()
    root.title("TechVenda - Emitir Cupom")
    root.geometry("420x280")
    root.configure(bg="#0f0f1a")
    root.resizable(False, False)

    tk.Label(root, text="EMISSÃO DE CUPOM", font=("Arial", 18, "bold"), 
             bg="#0f0f1a", fg="#67e8f9").pack(pady=20)

    tk.Label(root, text="Número do Pedido:", font=("Segoe UI", 12), 
             bg="#0f0f1a", fg="white").pack(pady=5)

    entry = tk.Entry(root, font=("Arial", 14), justify="center", width=15)
    entry.pack(pady=10)
    entry.focus()

    def ver():
        try:
            num = int(entry.get())
            exibir_cupom(num)
        except ValueError:
            messagebox.showerror("Erro", "Digite um número válido!")

    def salvar():
        try:
            num = int(entry.get())
            caminho = salvar_cupom(num)
            if caminho:
                messagebox.showinfo("Sucesso", f"Cupom salvo!\n{caminho}")
        except ValueError:
            messagebox.showerror("Erro", "Digite um número válido!")

    btn_frame = tk.Frame(root, bg="#0f0f1a")
    btn_frame.pack(pady=20)

    tk.Button(btn_frame, text="Ver Cupom", command=ver, bg="#22c55e", fg="white", 
              font=("Segoe UI", 11, "bold"), width=15, height=2).pack(side=tk.LEFT, padx=12)
    tk.Button(btn_frame, text="Salvar .txt", command=salvar, bg="#eab308", fg="white", 
              font=("Segoe UI", 11, "bold"), width=15, height=2).pack(side=tk.LEFT, padx=12)

    root.mainloop()


# Para ser chamado pelo menu principal
if __name__ == "__main__":
    abrir_menu()