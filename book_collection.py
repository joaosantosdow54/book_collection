import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
import pandas as pd

class BookCollectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Coleção de Livros")
        self.root.geometry("1200x800")
        
        # Set theme and style
        style = ttk.Style()
        style.configure("Custom.TLabelframe", padding=15)
        style.configure("Custom.TLabelframe.Label", font=("Helvetica", 12, "bold"))
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))
        style.configure("Summary.TLabel", font=("Helvetica", 11))
        
        # Initialize sort direction dictionary
        self.sort_direction = {}
        
        # Initialize database
        self.init_database()
        
        # Create main frame with padding
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=BOTH, expand=YES)
        
        # Create search and filter section
        self.create_search_filter()
        
        # Create input fields
        self.create_input_fields()
        
        # Create buttons
        self.create_buttons()
        
        # Create treeview
        self.create_treeview()
        
        # Create summary section
        self.create_summary()
        
        # Load initial data
        self.load_books()

    def init_database(self):
        self.conn = sqlite3.connect('livros.db')
        self.cursor = self.conn.cursor()
        
        # Create books table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS livros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                num_livros INTEGER,
                valor_euros REAL,
                livros_faltantes INTEGER,
                total_livros INTEGER,
                preco_medio REAL
            )
        ''')
        self.conn.commit()

    def create_search_filter(self):
        # Search and filter frame with custom style
        search_frame = ttk.LabelFrame(self.main_frame, text="Pesquisar e Filtrar", 
                                    style="Custom.TLabelframe", padding="15")
        search_frame.pack(fill=X, pady=10)
        
        # Create search entry with modern style
        ttk.Label(search_frame, text="Pesquisar:", style="Header.TLabel").pack(side=LEFT, padx=10)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=LEFT, padx=10, fill=X, expand=YES)
        
        # Create column filter combobox with modern style
        ttk.Label(search_frame, text="Filtrar por:", style="Header.TLabel").pack(side=LEFT, padx=10)
        self.filter_columns = ["Todos", "Nome", "Nº Livros", "Valor(€)", "Livros em Falta", 
                             "Total Livros", "Preço Médio(€)"]
        self.filter_var = tk.StringVar(value="Todos")
        self.filter_combo = ttk.Combobox(search_frame, textvariable=self.filter_var, 
                                       values=self.filter_columns, state="readonly", width=15)
        self.filter_combo.pack(side=LEFT, padx=10)
        
        # Create search and clear buttons with modern style
        ttk.Button(search_frame, text="Pesquisar", command=self.search_books, 
                  style="primary.TButton", width=15).pack(side=LEFT, padx=10)
        ttk.Button(search_frame, text="Limpar Filtros", command=self.clear_filters, 
                  style="secondary.TButton", width=15).pack(side=LEFT, padx=10)

    def create_input_fields(self):
        # Input frame with custom style
        input_frame = ttk.LabelFrame(self.main_frame, text="Detalhes do Livro", 
                                   style="Custom.TLabelframe", padding="15")
        input_frame.pack(fill=X, pady=10)
        
        # Create and grid input fields with modern style
        fields = [
            ("Nome:", "nome_entry"),
            ("Nº Livros:", "num_livros_entry"),
            ("Valor(€):", "valor_entry"),
            ("Livros em Falta:", "livros_faltantes_entry"),
            ("Total Livros:", "total_livros_entry"),
            ("Preço Médio(€):", "preco_medio_entry")
        ]
        
        for i, (label_text, entry_name) in enumerate(fields):
            ttk.Label(input_frame, text=label_text, style="Header.TLabel").grid(
                row=i//3, column=i%3*2, padx=15, pady=10, sticky=W)
            setattr(self, entry_name, ttk.Entry(input_frame, width=30))
            getattr(self, entry_name).grid(row=i//3, column=i%3*2+1, padx=15, pady=10, sticky=EW)
        
        for i in range(3):
            input_frame.columnconfigure(i*2+1, weight=1)

    def create_buttons(self):
        # Button frame with modern style
        button_frame = ttk.Frame(self.main_frame, padding="10")
        button_frame.pack(fill=X, pady=10)
        
        # Create buttons with modern style and icons
        ttk.Button(button_frame, text="Adicionar Livro", command=self.add_book, 
                  style="success.TButton", width=20).pack(side=LEFT, padx=10)
        ttk.Button(button_frame, text="Atualizar Livro", command=self.update_book, 
                  style="info.TButton", width=20).pack(side=LEFT, padx=10)
        ttk.Button(button_frame, text="Excluir Livro", command=self.delete_book, 
                  style="danger.TButton", width=20).pack(side=LEFT, padx=10)
        ttk.Button(button_frame, text="Limpar Campos", command=self.clear_fields, 
                  style="secondary.TButton", width=20).pack(side=LEFT, padx=10)
        ttk.Button(button_frame, text="Importar Excel", command=self.import_excel, 
                  style="primary.TButton", width=20).pack(side=LEFT, padx=10)

    def create_treeview(self):
        # Treeview frame with modern style
        tree_frame = ttk.Frame(self.main_frame, padding="10")
        tree_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        # Create treeview with modern style
        columns = ("ID", "Nome", "Nº Livros", "Valor(€)", "Livros em Falta", 
                  "Total Livros", "Preço Médio(€)")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", 
                                style="primary.Treeview")
        
        # Set column headings and bind click events
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
            self.tree.column(col, width=100, anchor=CENTER)
        
        # Add scrollbar with modern style
        scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.tree.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Bind select event
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def create_summary(self):
        # Summary frame with custom style
        summary_frame = ttk.LabelFrame(self.main_frame, text="Resumo", 
                                     style="Custom.TLabelframe", padding="15")
        summary_frame.pack(fill=X, pady=10)
        
        # Create labels for summary information with modern style
        self.total_books_label = ttk.Label(summary_frame, text="Total de Livros: 0", 
                                         style="Summary.TLabel")
        self.total_books_label.pack(side=LEFT, padx=30)
        
        self.total_value_label = ttk.Label(summary_frame, text="Valor Total: 0.00 €", 
                                         style="Summary.TLabel")
        self.total_value_label.pack(side=LEFT, padx=30)
        
        self.avg_price_label = ttk.Label(summary_frame, text="Preço Médio: 0.00 €", 
                                       style="Summary.TLabel")
        self.avg_price_label.pack(side=LEFT, padx=30)
        
        self.missing_books_label = ttk.Label(summary_frame, text="Livros em Falta: 0", 
                                           style="Summary.TLabel")
        self.missing_books_label.pack(side=LEFT, padx=30)

    def update_summary(self):
        try:
            # Get total books and value
            self.cursor.execute('''
                SELECT 
                    SUM(total_livros) as total_books,
                    SUM(valor_euros) as total_value,
                    AVG(preco_medio) as avg_price,
                    SUM(livros_faltantes) as missing_books
                FROM livros
            ''')
            result = self.cursor.fetchone()
            
            # Update labels with formatted values
            self.total_books_label.config(text=f"Total de Livros: {result[0] or 0}")
            self.total_value_label.config(text=f"Valor Total: {result[1] or 0:.2f} €")
            self.avg_price_label.config(text=f"Preço Médio: {result[2] or 0:.2f} €")
            self.missing_books_label.config(text=f"Livros em Falta: {result[3] or 0}")
            
        except Exception as e:
            print(f"Erro ao atualizar resumo: {str(e)}")

    def load_books(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load books from database
        self.cursor.execute("SELECT * FROM livros")
        for book in self.cursor.fetchall():
            self.tree.insert("", END, values=book)
        
        # Update summary
        self.update_summary()
        
        # Reset sort direction indicators
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
            self.sort_direction[col] = False

    def add_book(self):
        try:
            # Get values from entries
            nome = self.nome_entry.get().strip()
            num_livros = self.num_livros_entry.get().strip()
            valor = self.valor_entry.get().strip()
            livros_faltantes = self.livros_faltantes_entry.get().strip()
            total_livros = self.total_livros_entry.get().strip()
            preco_medio = self.preco_medio_entry.get().strip()

            # Check if all fields are empty
            if not any([nome, num_livros, valor, livros_faltantes, total_livros, preco_medio]):
                messagebox.showerror("Erro", "Pelo menos um campo deve ser preenchido!")
                return

            # Convert numeric values with proper error handling
            try:
                num_livros = int(num_livros) if num_livros else 0
            except ValueError:
                num_livros = 0

            try:
                valor = float(valor) if valor else 0.0
            except ValueError:
                valor = 0.0

            try:
                livros_faltantes = int(livros_faltantes) if livros_faltantes else 0
            except ValueError:
                livros_faltantes = 0

            try:
                total_livros = int(total_livros) if total_livros else 0
            except ValueError:
                total_livros = 0

            try:
                preco_medio = float(preco_medio) if preco_medio else 0.0
            except ValueError:
                preco_medio = 0.0

            values = (
                nome,
                num_livros,
                valor,
                livros_faltantes,
                total_livros,
                preco_medio
            )
            
            # Insert into database
            self.cursor.execute('''
                INSERT INTO livros (nome, num_livros, valor_euros, livros_faltantes, 
                                 total_livros, preco_medio)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', values)
            self.conn.commit()
            
            # Reload books and clear fields
            self.load_books()
            self.clear_fields()
            messagebox.showinfo("Sucesso", "Livro adicionado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar livro: {str(e)}")

    def update_book(self):
        try:
            # Get selected item
            selected_item = self.tree.selection()[0]
            book_id = self.tree.item(selected_item)['values'][0]
            
            # Get values from entries
            values = (
                self.nome_entry.get(),
                int(self.num_livros_entry.get() or 0),
                float(self.valor_entry.get() or 0),
                int(self.livros_faltantes_entry.get() or 0),
                int(self.total_livros_entry.get() or 0),
                float(self.preco_medio_entry.get() or 0),
                book_id
            )
            
            # Update database
            self.cursor.execute('''
                UPDATE livros
                SET nome=?, num_livros=?, valor_euros=?, livros_faltantes=?,
                    total_livros=?, preco_medio=?
                WHERE id=?
            ''', values)
            self.conn.commit()
            
            # Reload books and clear fields
            self.load_books()
            self.clear_fields()
            messagebox.showinfo("Sucesso", "Livro atualizado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar livro: {str(e)}")

    def delete_book(self):
        try:
            # Get selected item
            selected_item = self.tree.selection()[0]
            book_id = self.tree.item(selected_item)['values'][0]
            
            # Confirm deletion
            if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este livro?"):
                # Delete from database
                self.cursor.execute("DELETE FROM livros WHERE id=?", (book_id,))
                self.conn.commit()
                
                # Reload books and clear fields
                self.load_books()
                self.clear_fields()
                messagebox.showinfo("Sucesso", "Livro excluído com sucesso!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir livro: {str(e)}")

    def clear_fields(self):
        # Clear all entry fields
        for entry in [self.nome_entry, self.num_livros_entry, self.valor_entry,
                     self.livros_faltantes_entry, self.total_livros_entry, self.preco_medio_entry]:
            entry.delete(0, END)

    def on_select(self, event):
        # Get selected item
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item)['values']
        
        # Update entry fields
        self.nome_entry.delete(0, END)
        self.nome_entry.insert(0, values[1])
        
        self.num_livros_entry.delete(0, END)
        self.num_livros_entry.insert(0, values[2])
        
        self.valor_entry.delete(0, END)
        self.valor_entry.insert(0, values[3])
        
        self.livros_faltantes_entry.delete(0, END)
        self.livros_faltantes_entry.insert(0, values[4])
        
        self.total_livros_entry.delete(0, END)
        self.total_livros_entry.insert(0, values[5])
        
        self.preco_medio_entry.delete(0, END)
        self.preco_medio_entry.insert(0, values[6])

    def import_excel(self):
        try:
            # Open file dialog
            file_path = filedialog.askopenfilename(
                filetypes=[("Arquivos Excel", "*.xlsx *.xls")]
            )
            
            if not file_path:
                return
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Fill NaN values with appropriate defaults
            df = df.fillna({
                'NOME': '',
                'Nº LIVROS': 0,
                'VALOR(€)': 0.0,
                'LIVROS EM FALTA': 0,
                'TOTAL LIVROS': 0,
                'PREÇO MÉDIO(€)': 0.0
            })
            
            # Insert data into database
            for _, row in df.iterrows():
                try:
                    # Get values with defaults if columns don't exist
                    nome = str(row.get('NOME', ''))
                    num_livros = int(float(row.get('Nº LIVROS', 0)))
                    valor = float(row.get('VALOR(€)', 0.0))
                    livros_faltantes = int(float(row.get('LIVROS EM FALTA', 0)))
                    total_livros = int(float(row.get('TOTAL LIVROS', 0)))
                    preco_medio = float(row.get('PREÇO MÉDIO(€)', 0.0))
                    
                    values = (nome, num_livros, valor, livros_faltantes, total_livros, preco_medio)
                    
                    self.cursor.execute('''
                        INSERT INTO livros (
                            nome, num_livros, valor_euros, livros_faltantes,
                            total_livros, preco_medio
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', values)
                except Exception as row_error:
                    print(f"Erro ao processar linha: {row_error}")
                    continue
            
            self.conn.commit()
            self.load_books()
            messagebox.showinfo("Sucesso", f"Importados {len(df)} registros com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao importar arquivo Excel: {str(e)}")

    def search_books(self):
        search_text = self.search_var.get().strip().lower()
        filter_column = self.filter_var.get()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search_text:
            self.load_books()
            return
        
        # Build the query based on the selected filter
        if filter_column == "Todos":
            query = '''
                SELECT * FROM livros 
                WHERE LOWER(nome) LIKE ?
            '''
            params = [f'%{search_text}%']
        else:
            # Map filter column names to database column names
            column_map = {
                "Nome": "nome",
                "Nº Livros": "num_livros",
                "Valor(€)": "valor_euros",
                "Livros em Falta": "livros_faltantes",
                "Total Livros": "total_livros",
                "Preço Médio(€)": "preco_medio"
            }
            
            db_column = column_map[filter_column]
            query = f'SELECT * FROM livros WHERE LOWER({db_column}) LIKE ?'
            params = [f'%{search_text}%']
        
        # Execute the search
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        
        # Display results
        for book in results:
            self.tree.insert("", END, values=book)
        
        # Update summary with filtered results
        self.update_summary_filtered(results)

    def update_summary_filtered(self, results):
        try:
            if not results:
                # If no results, show zeros
                self.total_books_label.config(text="Total de Livros: 0")
                self.total_value_label.config(text="Valor Total: 0.00 €")
                self.avg_price_label.config(text="Preço Médio: 0.00 €")
                self.missing_books_label.config(text="Livros em Falta: 0")
                return
            
            # Calculate totals from filtered results
            total_books = sum(row[5] for row in results)  # total_livros column
            total_value = sum(row[3] for row in results)  # valor_euros column
            avg_price = total_value / total_books if total_books > 0 else 0
            missing_books = sum(row[4] for row in results)  # livros_faltantes column
            
            # Update labels
            self.total_books_label.config(text=f"Total de Livros: {total_books}")
            self.total_value_label.config(text=f"Valor Total: {total_value:.2f} €")
            self.avg_price_label.config(text=f"Preço Médio: {avg_price:.2f} €")
            self.missing_books_label.config(text=f"Livros em Falta: {missing_books}")
            
        except Exception as e:
            print(f"Erro ao atualizar resumo filtrado: {str(e)}")

    def clear_filters(self):
        self.search_var.set("")
        self.filter_var.set("Todos")
        self.load_books()

    def sort_treeview(self, col):
        # Get all items from treeview
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        
        # Convert values based on column type
        def convert_value(value):
            if col in ["ID", "Nº Livros", "Livros em Falta", "Total Livros"]:
                try:
                    return int(value) if value else 0
                except ValueError:
                    return 0
            elif col in ["Valor(€)", "Preço Médio(€)"]:
                try:
                    return float(value) if value else 0.0
                except ValueError:
                    return 0.0
            else:
                return str(value).lower() if value else ""
        
        # Sort items with converted values
        items.sort(key=lambda x: convert_value(x[0]), reverse=self.sort_direction[col])
        
        # Toggle sort direction for next click
        self.sort_direction[col] = not self.sort_direction[col]
        
        # Rearrange items in sorted positions
        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)
        
        # Update column header to show sort direction
        for column in self.tree['columns']:
            if column == col:
                direction = "↓" if self.sort_direction[col] else "↑"
                self.tree.heading(column, text=f"{column} {direction}")
            else:
                self.tree.heading(column, text=column)

if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")
    app = BookCollectionApp(root)
    root.mainloop() 