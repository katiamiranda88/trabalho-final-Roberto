#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Emissão de Cupom - TechVenda
Compatível com o menu principal (modulomenu.py)
"""

import os
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import mysql.connector
from mysql.connector import Error


# ==================== CONFIGURAÇÃO DO BANCO ====================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'techvenda_db'
}


def buscar_dados_pedido(id_pedido):
    """Busca dados do pedido para gerar o cupom."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT p.id_pedido, p.data_pedido, p.quantidade, p.status_pedido,
               c.nome AS nome_cliente, pr.nome_produto, pr.preco,
               (p.quantidade * pr.preco) AS total
        FROM pedidos p
        JOIN clientes c ON p.id_cliente = c.id_cliente
        JOIN produtos pr ON p.id_produto = pr.id_produto
        WHERE p.id_pedido = %s
        """
        cursor.execute(query, (id_pedido,))
        return cursor.fetchone()
    except Error as e:
        print(f"Erro ao buscar pedido: {e}")
        return None
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


def formatar_moeda(valor):
    """Formata valor para moeda brasileira."""
    return f"R${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def montar_cupom(dados):
    """Monta o cupom formatado com 48 caracteres."""
    if not dados:
        return "ERRO: Pedido não encontrado."
    
    largura = 48
    sep = "=" * largura
    div = "-" * largura
    
    cupom = f"{sep}\n"
    cupom += "TECHVENDA LTDA.".center(largura) + "\n"
    cupom += "Dist. de Informatica — CNPJ: 00.000/0001-00".center(largura) + "\n"
    cupom += f"{sep}\n\n"

    data_str = dados['data_pedido'].strftime("%d/%m/%Y %H:%M") if isinstance(dados['data_pedido'], datetime.datetime) else str(dados['data_pedido'])
    
    cupom += f"PEDIDO Nº: {str(dados['id_pedido']).zfill(4)} DATA: {data_str}\n"
    cupom += f"CLIENTE: {dados['nome_cliente']}\n"
    cupom += f"{div}\n"
    cupom += "PRODUTO".ljust(28) + "QTD".ljust(6) + "UNIT".ljust(8) + "TOTAL".ljust(8) + "\n"
    cupom += f"{div}\n"

    nome = str(dados['nome_produto'])[:25]
    qtd = str(dados['quantidade'])
    unit = formatar_moeda(dados['preco'])
    total_item = formatar_moeda(dados['total'])

    cupom += nome.ljust(28) + qtd.ljust(6) + unit.rjust(8) + total_item.rjust(8) + "\n"
    cupom += f"{div}\n"
    cupom += f"TOTAL GERAL: {formatar_moeda(dados['total'])}\n"
    cupom += f"{sep}\n"

    status = dados.get('status_pedido', 'Pendente')
    cupom += f"Status: {status}\n"
    cupom += "Obrigado pela preferencia! Volte sempre.\n"
    agora = datetime.datetime.now()
    cupom += f"Emitido em: {agora.strftime('%d/%m/%Y as %H:%M:%S')}\n"
    cupom += f"{sep}\n"
    
    return cupom


def salvar_cupom(id_pedido, pasta='cupons'):
    """Salva cupom em arquivo."""
    try:
        dados = buscar_dados_pedido(id_pedido)
        if not dados:
            messagebox.showerror("Erro", "Pedido não encontrado.")
            return None
        
        texto = montar_cupom(dados)
        os.makedirs(pasta, exist_ok=True)
        
        agora = datetime.datetime.now()
        nome = f"cupom_{str(id_pedido).zfill(4)}_{agora.strftime('%Y%m%d_%H%M%S')}.txt"
        caminho = os.path.join(pasta, nome)
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(texto)
        
        messagebox.showinfo("Sucesso", f"Cupom salvo em:\n{caminho}")
        return caminho
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar cupom: {e}")
        return None


def exibir_cupom_tela(id_pedido):
    """Exibe o cupom em janela."""
    try:
        dados = buscar_dados_pedido(id_pedido)
        if not dados:
            messagebox.showerror("Erro", "Pedido não encontrado.")
            return
        
        texto = montar_cupom(dados)
        
        janela = tk.Toplevel()
        janela.title(f"Cupom - Pedido {id_pedido}")
        janela.geometry("640x580")
        
        text_area = scrolledtext.ScrolledText(janela, font=("Courier", 10), wrap=tk.NONE, width=80, height=30)
        text_area.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        text_area.insert(tk.END, texto)
        text_area.config(state=tk.DISABLED)
        
        btn_frame = ttk.Frame(janela)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Salvar .txt", command=lambda: salvar_cupom(id_pedido)).pack(side=tk.LEFT, padx=15)
        ttk.Button(btn_frame, text="Fechar", command=janela.destroy).pack(side=tk.RIGHT, padx=15)
    except Exception as e:
        messagebox.showerror("Erro", str(e))


# ===================== FUNÇÃO PRINCIPAL (CHAMADA PELO MENU) =====================
def abrir_emissor_cupom():
    """Função principal chamada pelo botão 'Emitir Cupom' no menu."""
    try:
        root = tk.Tk()
        root.title("TechVenda - Emitir Cupom")
        root.geometry("480x280")
        root.resizable(False, False)
        
        ttk.Label(root, text="Emitir Cupom de Venda", font=("Arial", 16, "bold")).pack(pady=20)
        ttk.Label(root, text="Digite o Número do Pedido:", font=("Segoe UI", 11)).pack(pady=5)
        
        entry = ttk.Entry(root, width=30, font=("Arial", 12))
        entry.pack(pady=8)
        entry.focus()
        
        def ver_cupom():
            try:
                pid = int(entry.get().strip())
                exibir_cupom_tela(pid)
            except:
                messagebox.showerror("Erro", "Número de pedido inválido!")
        
        def salvar_direto():
            try:
                pid = int(entry.get().strip())
                salvar_cupom(pid)
            except:
                messagebox.showerror("Erro", "Número de pedido inválido!")
        
        frame_btn = ttk.Frame(root)
        frame_btn.pack(pady=25)
        
        ttk.Button(frame_btn, text="Ver Cupom", command=ver_cupom).pack(side=tk.LEFT, padx=12)
        ttk.Button(frame_btn, text="Salvar .txt", command=salvar_direto).pack(side=tk.LEFT, padx=12)
        ttk.Button(frame_btn, text="Fechar", command=root.destroy).pack(side=tk.LEFT, padx=12)
        
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir emissor:\n{e}")


# Compatibilidade com o menu principal
abrir_menu = abrir_emissor_cupom   # Alias importante para o modulomenu.py


# Execução direta
if __name__ == "__main__":
    abrir_emissor_cupom()