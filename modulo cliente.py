import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

def conectar():
    conn = sqlite3.connect("techvenda.db")
    return conn

def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS clientes(
                       id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                       nome         TEX     NOT NULL,
                       email        TEXT,
                       telefone     TEXT,
                       cidade       TEXT,
                       data_cadastro TEXT
                   )
               """)
    conn.commit()
    conn.close()
    
def salvar():
    nome        = entry_nome.get()
    email       = entry_email.get()
    telefone    = entry_telefone.get()
    cidade      = entry_cidade.get()
    data        = str(date.today())
    
    if not nome:
        messagebox.showwarning("Atenção", "o campo nome é obrigatório!")
        return
    conn   = conectar()
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT INTO clientes (nome, email, telefone, cidade, data_cadastro)
                   
                   VALUES (?, ?, ?, ?, ?)
                   
                """, (nome, email, telefone, cidade, data))
    #Insere o novo cliente na tabela do banco
    conn.commit()
    conn.close()
                
    messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
    limpar_campos()
    listar()
    
def alterar():
    id_cliente = entry_id.get()
    
    if not id_cliente:
        messagebox.showwarning("Altenção", "Informe o ID do cliente para alterar")
        
        return
    
    nome        = entry_nome.get()
    email       = entry_email.get()
    telefone    = entry_telefone.get()
    cidade      = entry_cidade.get()
    
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
            UPDATE clientes
                   SET nome=?, email=?, telefone=?, cidade=?
            WHERE id_clientes=?
        """, (nome, email, telefone, cidade, id_cliente)) 

    conn.commit()
    conn.close()
    
    messagebox.showinfo("Sucesso", "Cliente alterado com sucesso!")
    limpar_campos()
    listar()
    
def excluir():
    id_cliente = entry_id.get()
    
    if not id_cliente:
        messagebox.showwarning("Atenção", "Informe o ID do cliente para excluir!")
        
        return
    
    confirmar = messagebox.askyesno("Confirmar", f"Deseja realmente excluir o cliente ID{id_cliente}?")
    
    if not confirmar:
        
        return
    
    conn = conectar
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id_cliente=?",
                   (id_cliente,))
    
    conn.commit()
    conn.close()
    
    messagebox.showinfo("Sucesso", "Cliente excluido com sucesso!")
    
    limpar_campos()
    listar()
    
def listar():
    for row in tree.get_children():
        tree.delete(row)
        
    conn  = connectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes ORDER BY nome")
    
    registros = cursor.fetchall()
    conn.close()
    
    for reg in registros:
        tree.insert("", tk.END, values=reg)
        
def limpar_campos():
    entry_id.delete(0, tk.END)
    entry_nome.delete(0, tk.END)
    entry_email.delete(0, tk.END)
    entry_telefone.delete(0, tk.END)
    entry_cidade.delete(0, tk.END)
    
def preencher_formular(event):
    selecionado = tree.focus()
    if not selecionado:
        
        return
    
    valores = tree.item(selecionado, "values")
    limpar_campos()
    entry_id.insert(0, valores[0])
    entry_nome.insert(0, valores[1])
    entry_email.insert(0, valores[2])
    entry_telefone.insert(0, valores[3])
    entry_cidade.insert(0, valores[4])
    
def abrir(root):
    global entry_id, entry_nome, entry_email
    global entry_telefone, entry_cidade, tree 
    
    criar_tabela()
    
    janela = tk.Toplevel(root)
    janela.title("Cadastro de Clientes - TechVenda")
    janela.geometry("860x560")
    janela.resizable(True, True)
    janela.configure(bg="#f0f4f8")

    frame_from = tk.LabelFrame(janela,
        text=" Dados do Cliente ",
        bg="#f0f4f8", fg="#1a1a2e",
        font=("Arial", 10, "bold"), padx=10, pady=10)
    frame_form.pack(fill="x", padx=20, pady=10)
        
    tk.Label(frame_form, text="ID:", 
        bg="#f0f4f8",
                    font=("Arial", 9)).grid(row=0, 
        column=0, sticky="e", padx=5, pady=4)
            
    entry_id = tk.Entry(frame_form, width=8,
        font=("Arial", 9))
    entry_id.grid(row=0, column=1, sticky="w", padx=5, pady=4)
            
    tk.Label(frame_form, text="Nome:",
        bg="#f0f4f8",
                    font=("Arial", 9)).grid(row=0, 
                                            column=2, stick="e", padx=5, pady=4)
    entry_nome = tk.Entry(frame_form, width=30, font=("Arial", 9))
    entry_nome.grid(row=0, column=3, sticky="w", padx=5, pady=4)
            
    tk.Label(frame_form, text="E-mail:",
        bg="#f0f4f8",
                    font=(Arial, 9)).grid(row=1, column=3, sticky="e", padx=5, pady=4)
    entry_telefone = tk.Entry(frame_form, width=18, font=("Arial, 9"))
    entry_telefone.grid(row=1, column=4, sticky="w", padx=5, pady=4)
            
    tk.Label(frame_form, text="Cidade:",
        bg="#f0f4f8", font=("Arial", 9)).grid(row=2, column=0, sticky="e, padx=5, pady=4")
    
    entry_cidade = tk.Entry(frame_form, width=30, font=("Arial", 9))
        
    entry_cidade.grid(row=2, column=1, columnspan=2, sticky="w", padx=5, pady=4)

    
    
