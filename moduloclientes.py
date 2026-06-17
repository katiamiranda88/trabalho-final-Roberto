# modulo_clientes.py
# Gestão de Clientes - TechVenda Ltda.

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector


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
    if messagebox.askokcancel('Voltar ao Menu', 'Deseja voltar ao menu principal?\nDados não salvos serão perdidos.'):
        janela.destroy()
        try:
            import modulomenu
            modulomenu.abrir_menu()
        except Exception:
            messagebox.showerror("Erro", "Não foi possível abrir o menu principal.")


class AppClientes:
    def __init__(self, root):
        self.root = root
        self.root.title("TechVenda — Gestão de Clientes")
        self.root.geometry("1280x760")
        self.root.resizable(True, True)
        self.root.configure(bg="#0f0f1a")

        self.id_selecionado = None
        self.var_busca = tk.StringVar()

        self.criar_interface()
        self.carregar_clientes()   # Carrega automaticamente


    def criar_interface(self):
        # HEADER
        header = tk.Frame(self.root, bg="#1a1a2e", height=85)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Button(header, text="← VOLTAR AO MENU", bg="#c0392b", fg="white",
                  font=("Arial", 11, "bold"), relief="flat", padx=20, pady=8,
                  command=lambda: voltar(self.root)).pack(side="left", padx=25, pady=20)

        tk.Label(header, text="👥 GESTÃO DE CLIENTES", font=("Arial", 24, "bold"),
                 bg="#1a1a2e", fg="#00d4ff").pack(side="left", padx=20, pady=20)

        # Busca
        busca_frame = tk.Frame(header, bg="#1a1a2e")
        busca_frame.pack(side="right", padx=40)
        tk.Label(busca_frame, text="🔍 Buscar:", bg="#1a1a2e", fg="#aaaaaa").pack(side="left")
        ttk.Entry(busca_frame, textvariable=self.var_busca, width=45).pack(side="left", padx=10)
        self.var_busca.trace("w", lambda *args: self.carregar_clientes())

        # Área Principal
        main_frame = tk.Frame(self.root, bg="#0f0f1a", padx=35, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Formulário Esquerdo
        form_frame = tk.LabelFrame(main_frame, text=" Dados do Cliente ", 
                                 bg="#16213e", fg="#ffffff", font=("Segoe UI", 12, "bold"), padx=25, pady=25)
        form_frame.pack(side="left", fill="y", padx=(0, 30))

        campos = [
            ("ID", None),
            ("Nome *", "entry_nome"),
            ("E-mail", "entry_email"),
            ("Telefone", "entry_telefone"),
            ("Cidade", "entry_cidade")
        ]

        self.entries = {}
        for i, (label_text, var_name) in enumerate(campos):
            tk.Label(form_frame, text=label_text, bg="#16213e", fg="#cccccc", font=("Segoe UI", 11)).grid(
                row=i, column=0, sticky="w", pady=10)
            
            if var_name:
                entry = ttk.Entry(form_frame, width=42, font=("Segoe UI", 11))
                entry.grid(row=i, column=1, padx=20, pady=10, sticky="ew")
                self.entries[var_name] = entry
            else:
                self.lbl_id = tk.Label(form_frame, text="---", bg="#16213e", fg="#00ff9d", 
                                     font=("Arial", 12, "bold"))
                self.lbl_id.grid(row=i, column=1, sticky="w", padx=20, pady=10)

        # Botões
        btn_frame = tk.Frame(form_frame, bg="#16213e")
        btn_frame.grid(row=len(campos), column=0, columnspan=2, pady=30)

        ttk.Button(btn_frame, text="💾 SALVAR", command=self.salvar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✏️ ALTERAR", command=self.alterar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑 EXCLUIR", command=self.excluir).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🧹 LIMPAR", command=self.limpar).pack(side="left", padx=5)

        # Lista de Clientes (Direita)
        list_frame = tk.LabelFrame(main_frame, text=" Clientes Cadastrados ", 
                                 bg="#16213e", fg="#ffffff", font=("Segoe UI", 12, "bold"), padx=20, pady=20)
        list_frame.pack(side="right", fill="both", expand=True)

        cols = ("ID", "Nome", "E-mail", "Telefone", "Cidade")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings")
        
        widths = {"ID": 80, "Nome": 260, "E-mail": 280, "Telefone": 150, "Cidade": 200}
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths.get(col, 140), anchor="w")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.selecionar)

        self.entries["entry_nome"].focus()


    def carregar_clientes(self, *args):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = conectar_db()
        if not conn: return
        try:
            cursor = conn.cursor()
            busca = self.var_busca.get().strip()
            
            if busca:
                cursor.execute("""
                    SELECT id_cliente, nome, email, telefone, cidade 
                    FROM clientes 
                    WHERE nome LIKE %s OR email LIKE %s 
                    ORDER BY nome
                """, (f"%{busca}%", f"%{busca}%"))
            else:
                cursor.execute("""
                    SELECT id_cliente, nome, email, telefone, cidade 
                    FROM clientes ORDER BY nome
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
        
        self.id_selecionado = valores[0]
        self.lbl_id.config(text=valores[0])

        self.entries["entry_nome"].delete(0, tk.END)
        self.entries["entry_nome"].insert(0, valores[1])
        self.entries["entry_email"].delete(0, tk.END)
        self.entries["entry_email"].insert(0, valores[2] or "")
        self.entries["entry_telefone"].delete(0, tk.END)
        self.entries["entry_telefone"].insert(0, valores[3] or "")
        self.entries["entry_cidade"].delete(0, tk.END)
        self.entries["entry_cidade"].insert(0, valores[4] or "")


    def salvar(self):
        if not self.entries["entry_nome"].get().strip():
            messagebox.showwarning("Aviso", "O campo Nome é obrigatório!")
            return

        conn = conectar_db()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clientes (nome, email, telefone, cidade, data_cadastro)
                VALUES (%s, %s, %s, %s, CURDATE())
            """, (
                self.entries["entry_nome"].get().strip(),
                self.entries["entry_email"].get().strip() or None,
                self.entries["entry_telefone"].get().strip() or None,
                self.entries["entry_cidade"].get().strip() or None
            ))
            conn.commit()
            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
            self.limpar()
            self.carregar_clientes()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar:\n{str(e)}")
        finally:
            conn.close()


    def alterar(self):
        if not self.id_selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente para alterar.")
            return
        conn = conectar_db()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE clientes 
                SET nome=%s, email=%s, telefone=%s, cidade=%s
                WHERE id_cliente = %s
            """, (
                self.entries["entry_nome"].get().strip(),
                self.entries["entry_email"].get().strip() or None,
                self.entries["entry_telefone"].get().strip() or None,
                self.entries["entry_cidade"].get().strip() or None,
                self.id_selecionado
            ))
            conn.commit()
            messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!")
            self.carregar_clientes()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar:\n{str(e)}")
        finally:
            conn.close()


    def excluir(self):
        if not self.id_selecionado or not messagebox.askyesno("Confirmação", "Excluir este cliente?"):
            return
        conn = conectar_db()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (self.id_selecionado,))
            conn.commit()
            messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")
            self.limpar()
            self.carregar_clientes()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir:\n{str(e)}")
        finally:
            conn.close()


    def limpar(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.lbl_id.config(text="---")
        self.id_selecionado = None
        self.entries["entry_nome"].focus()


if __name__ == "__main__":
    root = tk.Tk()
    AppClientes(root)
    root.mainloop()