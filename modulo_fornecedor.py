# modulo_fornecedor.py
# Gestão de Fornecedores — TechVenda Ltda.

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import os
import sys

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


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


def voltar(janela):
    """Função robusta para voltar ao menu principal"""
    if messagebox.askokcancel('Voltar ao Menu', 'Deseja voltar ao menu principal?\nDados não salvos serão perdidos.'):
        janela.destroy()
        try:
            import modulomenu
            
            # Tenta encontrar a classe correta
            if hasattr(modulomenu, 'AppMenuPrincipal'):
                root = tk.Tk()
                app = modulomenu.AppMenuPrincipal(root)
                root.mainloop()
            elif hasattr(modulomenu, 'AppMenu'):
                root = tk.Tk()
                app = modulomenu.AppMenu(root)
                root.mainloop()
            else:
                # Executa o arquivo diretamente como fallback
                import subprocess
                caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modulomenu.py")
                subprocess.Popen(["python", caminho])
                
        except ImportError:
            messagebox.showerror("Erro", "Não foi possível encontrar o arquivo 'modulomenu.py'.")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível voltar ao menu:\n{e}")


class AppFornecedores:
    def __init__(self, root):
        self.root = root
        self.root.title("TechVenda — Gestão de Fornecedores")
        self.root.geometry("1250x720")
        self.root.resizable(True, True)
        self.root.configure(bg="#0f0f1a")

        self.fornecedor_id_selecionado = None
        self.var_busca = tk.StringVar()

        self.criar_interface()
        self.carregar_fornecedores()

    def criar_interface(self):
        # Header
        header = tk.Frame(self.root, bg="#1a1a2e", height=85)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Button(header, text="← VOLTAR AO MENU", bg="#c0392b", fg="white",
                  font=("Arial", 11, "bold"), relief="flat", padx=20, pady=8,
                  command=lambda: voltar(self.root)).pack(side="left", padx=25, pady=20)

        tk.Label(header, text="🛒 GESTÃO DE FORNECEDORES", font=("Arial", 24, "bold"),
                 bg="#1a1a2e", fg="#00d4ff").pack(side="left", padx=20, pady=20)

        # Busca
        busca_frame = tk.Frame(header, bg="#1a1a2e")
        busca_frame.pack(side="right", padx=40)
        tk.Label(busca_frame, text="🔍 Buscar:", bg="#1a1a2e", fg="#aaaaaa").pack(side="left")
        ttk.Entry(busca_frame, textvariable=self.var_busca, width=45).pack(side="left", padx=10)
        self.var_busca.trace("w", lambda *args: self.carregar_fornecedores())

        main_frame = tk.Frame(self.root, bg="#0f0f1a", padx=35, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Formulário
        form_frame = tk.LabelFrame(main_frame, text=" Dados do Fornecedor ", 
                                 bg="#16213e", fg="#ffffff", font=("Segoe UI", 12, "bold"), padx=25, pady=25)
        form_frame.pack(side="left", fill="y", padx=(0, 30))

        campos = [
            ("ID", None),
            ("Nome da Empresa *", "entry_nome"),
            ("CNPJ", "entry_cnpj"),
            ("Contato", "entry_contato"),
            ("Telefone", "entry_telefone"),
            ("E-mail", "entry_email")
        ]

        self.entries = {}
        for i, (label_text, var_name) in enumerate(campos):
            tk.Label(form_frame, text=label_text, bg="#16213e", fg="#cccccc", 
                    font=("Segoe UI", 11)).grid(row=i, column=0, sticky="w", pady=10)
            
            if var_name:
                entry = ttk.Entry(form_frame, width=42, font=("Segoe UI", 11))
                entry.grid(row=i, column=1, padx=20, pady=10, sticky="ew")
                self.entries[var_name] = entry
            else:
                self.lbl_id = tk.Label(form_frame, text="---", bg="#16213e", fg="#00ff9d", 
                                     font=("Arial", 12, "bold"))
                self.lbl_id.grid(row=i, column=1, sticky="w", padx=20, pady=10)

        btn_frame = tk.Frame(form_frame, bg="#16213e")
        btn_frame.grid(row=len(campos), column=0, columnspan=2, pady=30)

        ttk.Button(btn_frame, text="💾 SALVAR", command=self.salvar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✏️ ALTERAR", command=self.alterar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑 EXCLUIR", command=self.excluir).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🧹 LIMPAR", command=self.limpar).pack(side="left", padx=5)

        # Lista
        list_frame = tk.LabelFrame(main_frame, text=" Fornecedores Cadastrados ", 
                                 bg="#16213e", fg="#ffffff", font=("Segoe UI", 12, "bold"), padx=20, pady=20)
        list_frame.pack(side="right", fill="both", expand=True)

        cols = ("ID", "Empresa", "CNPJ", "Contato", "Telefone", "E-mail")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings")
        
        widths = {"ID": 70, "Empresa": 280, "CNPJ": 150, "Contato": 160, "Telefone": 130, "E-mail": 240}
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths.get(col, 140), anchor="w")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.selecionar)

    def carregar_fornecedores(self, *args):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = conectar_db()
        if not conn: return
        try:
            cursor = conn.cursor()
            busca = self.var_busca.get().strip()
            
            if busca:
                cursor.execute("""
                    SELECT id_fornecedor, nome_fornecedor, CNPJ, contato, telefone, email 
                    FROM fornecedor 
                    WHERE nome_fornecedor LIKE %s OR CNPJ LIKE %s OR email LIKE %s
                    ORDER BY nome_fornecedor
                """, (f"%{busca}%", f"%{busca}%", f"%{busca}%"))
            else:
                cursor.execute("""
                    SELECT id_fornecedor, nome_fornecedor, CNPJ, contato, telefone, email 
                    FROM fornecedor ORDER BY nome_fornecedor
                """)
            
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Erro ao carregar", f"Erro:\n{str(e)}")
        finally:
            conn.close()

    def selecionar(self, event):
        sel = self.tree.selection()
        if not sel: return
        valores = self.tree.item(sel[0], "values")
        
        self.fornecedor_id_selecionado = valores[0]
        self.lbl_id.config(text=valores[0])

        for entry, value in zip(self.entries.values(), valores[1:]):
            entry.delete(0, tk.END)
            entry.insert(0, value or "")

    def salvar(self):
        nome = self.entries["entry_nome"].get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "Nome da Empresa é obrigatório!")
            return

        conn = conectar_db()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO fornecedor (nome_fornecedor, CNPJ, contato, telefone, email)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                nome,
                self.entries["entry_cnpj"].get().strip() or None,
                self.entries["entry_contato"].get().strip() or None,
                self.entries["entry_telefone"].get().strip() or None,
                self.entries["entry_email"].get().strip() or None
            ))
            conn.commit()
            messagebox.showinfo("Sucesso", "Fornecedor cadastrado com sucesso!")
            self.limpar()
            self.carregar_fornecedores()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar:\n{str(e)}")
        finally:
            conn.close()

    def alterar(self):
        if not self.fornecedor_id_selecionado:
            messagebox.showwarning("Aviso", "Selecione um fornecedor para alterar.")
            return

        conn = conectar_db()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE fornecedor 
                SET nome_fornecedor=%s, CNPJ=%s, contato=%s, telefone=%s, email=%s
                WHERE id_fornecedor = %s
            """, (
                self.entries["entry_nome"].get().strip(),
                self.entries["entry_cnpj"].get().strip() or None,
                self.entries["entry_contato"].get().strip() or None,
                self.entries["entry_telefone"].get().strip() or None,
                self.entries["entry_email"].get().strip() or None,
                self.fornecedor_id_selecionado
            ))
            conn.commit()
            messagebox.showinfo("Sucesso", "Fornecedor atualizado com sucesso!")
            self.carregar_fornecedores()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar:\n{str(e)}")
        finally:
            conn.close()

    def excluir(self):
        if not self.fornecedor_id_selecionado or not messagebox.askyesno("Confirmação", "Excluir este fornecedor?"):
            return
        conn = conectar_db()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM fornecedor WHERE id_fornecedor = %s", (self.fornecedor_id_selecionado,))
            conn.commit()
            messagebox.showinfo("Sucesso", "Fornecedor excluído com sucesso!")
            self.limpar()
            self.carregar_fornecedores()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir:\n{str(e)}")
        finally:
            conn.close()

    def limpar(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.lbl_id.config(text="---")
        self.fornecedor_id_selecionado = None
        self.entries["entry_nome"].focus()


if __name__ == "__main__":
    root = tk.Tk()
    app = AppFornecedores(root)
    root.mainloop()