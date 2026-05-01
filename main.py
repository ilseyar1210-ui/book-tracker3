import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# ===== КОНСТАНТЫ =====
DATA_FILE = "books_data.json"

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Трекер прочитанных книг")
        self.root.geometry("950x650")
        self.root.resizable(False, False)

        self.books = self.load_books()
        self.current_filter_genre = ""
        self.current_filter_pages = None

        self.create_widgets()
        self.update_display()

    # ===== РАБОТА С JSON =====
    def load_books(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка загрузки: {e}")
                return []
        return []

    def save_books(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    # ===== ВАЛИДАЦИЯ =====
    def validate_pages(self, pages_str):
        try:
            pages = int(pages_str)
            return pages > 0, pages
        except ValueError:
            return False, None

    def validate_not_empty(self, value):
        return value is not None and value.strip() != ""

    # ===== ИНТЕРФЕЙС =====
    def create_widgets(self):
        # Рамка добавления книги
        add_frame = ttk.LabelFrame(self.root, text="📚 Добавить книгу", padding=15)
        add_frame.pack(fill="x", padx=10, pady=5)

        # Название
        ttk.Label(add_frame, text="Название книги:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=8, sticky="e")
        self.title_entry = ttk.Entry(add_frame, width=35, font=("Arial", 10))
        self.title_entry.grid(row=0, column=1, padx=5, pady=8)

        # Автор
        ttk.Label(add_frame, text="Автор:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=8, sticky="e")
        self.author_entry = ttk.Entry(add_frame, width=25, font=("Arial", 10))
        self.author_entry.grid(row=0, column=3, padx=5, pady=8)

        # Жанр
        ttk.Label(add_frame, text="Жанр:", font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=8, sticky="e")
        self.genre_var = tk.StringVar()
        genres = ["Роман", "Детектив", "Фантастика", "Наука", "Поэзия", 
                  "Биография", "Приключения", "Классика", "Триллер", "Другое"]
        genre_combo = ttk.Combobox(add_frame, textvariable=self.genre_var, 
                                    values=genres, width=23, state="readonly", font=("Arial", 10))
        genre_combo.grid(row=1, column=1, padx=5, pady=8)
        genre_combo.set("Роман")

        # Количество страниц
        ttk.Label(add_frame, text="Кол-во страниц:", font=("Arial", 10)).grid(row=1, column=2, padx=5, pady=8, sticky="e")
        self.pages_entry = ttk.Entry(add_frame, width=12, font=("Arial", 10))
        self.pages_entry.grid(row=1, column=3, padx=5, pady=8)

        # Кнопка добавления
        self.add_btn = ttk.Button(add_frame, text="➕ Добавить книгу", command=self.add_book, width=20)
        self.add_btn.grid(row=2, column=0, columnspan=4, pady=12)

        # Рамка фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="🔍 Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Жанр:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.filter_genre_var = tk.StringVar()
        filter_genres = ["Все"] + ["Роман", "Детектив", "Фантастика", "Наука", "Поэзия", 
                                    "Биография", "Приключения", "Классика", "Триллер", "Другое"]
        filter_genre_combo = ttk.Combobox(filter_frame, textvariable=self.filter_genre_var,
                                           values=filter_genres, width=15, state="readonly")
        filter_genre_combo.grid(row=0, column=1, padx=5, pady=5)
        filter_genre_combo.set("Все")
        filter_genre_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())

        ttk.Label(filter_frame, text="Страниц больше:", font=("Arial", 10)).grid(row=0, column=2, padx=10, pady=5, sticky="e")
        self.filter_pages_entry = ttk.Entry(filter_frame, width=10, font=("Arial", 10))
        self.filter_pages_entry.grid(row=0, column=3, padx=5, pady=5)
        self.filter_pages_entry.bind("<KeyRelease>", lambda e: self.apply_filter())

        self.reset_btn = ttk.Button(filter_frame, text="🔄 Сбросить фильтр", command=self.reset_filter)
        self.reset_btn.grid(row=0, column=4, padx=15, pady=5)

        # Рамка списка книг
        books_frame = ttk.LabelFrame(self.root, text="📖 Список прочитанных книг", padding=10)
        books_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Таблица с прокруткой
        container = ttk.Frame(books_frame)
        container.pack(fill="both", expand=True)

        scrollbar_y = ttk.Scrollbar(container, orient="vertical")
        scrollbar_x = ttk.Scrollbar(container, orient="horizontal")

        columns = ("№", "Название", "Автор", "Жанр", "Страниц", "Дата добавления")
        self.tree = ttk.Treeview(container, columns=columns, show="headings", 
                                  yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set, height=12)
        
        col_widths = [40, 280, 160, 120, 80, 160]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="w")

        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Кнопки управления
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)

        self.delete_btn = ttk.Button(btn_frame, text="❌ Удалить выбранную", command=self.delete_book)
        self.delete_btn.pack(side="left", padx=5)

        self.clear_btn = ttk.Button(btn_frame, text="🗑 Очистить весь список", command=self.clear_all)
        self.clear_btn.pack(side="left", padx=5)

        self.stats_btn = ttk.Button(btn_frame, text="📊 Статистика", command=self.show_stats)
        self.stats_btn.pack(side="right", padx=5)

    # ===== ДОБАВЛЕНИЕ КНИГИ =====
    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_var.get()
        pages_str = self.pages_entry.get().strip()

        # Валидация
        if not self.validate_not_empty(title):
            messagebox.showwarning("Ошибка", "Название книги не может быть пустым!")
            return
        if not self.validate_not_empty(author):
            messagebox.showwarning("Ошибка", "Автор не может быть пустым!")
            return
        if not genre:
            messagebox.showwarning("Ошибка", "Выберите жанр!")
            return
        
        is_valid, pages = self.validate_pages(pages_str)
        if not is_valid:
            messagebox.showwarning("Ошибка", "Количество страниц должно быть положительным числом!")
            return

        # Добавление
        book = {
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages,
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.books.append(book)
        self.save_books()

        # Очистка полей
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)

        self.update_display()
        messagebox.showinfo("Успех", f"Книга «{title}» добавлена!")

    # ===== ФИЛЬТРАЦИЯ =====
    def apply_filter(self):
        genre = self.filter_genre_var.get()
        self.current_filter_genre = None if genre == "Все" else genre
        
        pages_str = self.filter_pages_entry.get().strip()
        if pages_str:
            try:
                self.current_filter_pages = int(pages_str)
            except ValueError:
                self.current_filter_pages = None
        else:
            self.current_filter_pages = None
        
        self.update_display()

    def reset_filter(self):
        self.filter_genre_var.set("Все")
        self.filter_pages_entry.delete(0, tk.END)
        self.current_filter_genre = None
        self.current_filter_pages = None
        self.update_display()

    # ===== ОТОБРАЖЕНИЕ =====
    def update_display(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        filtered = self.books.copy()

        if self.current_filter_genre:
            filtered = [b for b in filtered if b["genre"] == self.current_filter_genre]
        
        if self.current_filter_pages is not None:
            filtered = [b for b in filtered if b["pages"] > self.current_filter_pages]

        filtered.reverse()

        for idx, book in enumerate(filtered, 1):
            self.tree.insert("", "end", values=(
                idx,
                book["title"],
                book["author"],
                book["genre"],
                f"{book['pages']}",
                book["added_at"]
            ))

        # Обновляем заголовок
        if self.current_filter_genre or self.current_filter_pages:
            status = []
            if self.current_filter_genre:
                status.append(f"жанр={self.current_filter_genre}")
            if self.current_filter_pages:
                status.append(f"страниц > {self.current_filter_pages}")
            self.root.title(f"Book Tracker - Фильтр: {', '.join(status)}")
        else:
            self.root.title("Book Tracker - Трекер прочитанных книг")

    # ===== УДАЛЕНИЕ =====
    def delete_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите книгу для удаления")
            return

        item = self.tree.item(selected[0])
        title = item["values"][1]
        author = item["values"][2]

        for i, book in enumerate(self.books):
            if book["title"] == title and book["author"] == author:
                del self.books[i]
                break

        self.save_books()
        self.update_display()
        messagebox.showinfo("Успех", f"Книга «{title}» удалена")

    def clear_all(self):
        if not self.books:
            messagebox.showinfo("Инфо", "Список книг уже пуст")
            return

        if messagebox.askyesno("Подтверждение", "Удалить ВСЕ книги? Отменить нельзя!"):
            self.books.clear()
            self.save_books()
            self.reset_filter()
            self.update_display()
            messagebox.showinfo("Успех", "Список книг очищен")

    # ===== СТАТИСТИКА =====
    def show_stats(self):
        if not self.books:
            messagebox.showinfo("Статистика", "Нет добавленных книг")
            return

        total_books = len(self.books)
        total_pages = sum(b["pages"] for b in self.books)
        avg_pages = total_pages // total_books
        
        genres = {}
        authors = {}
        for book in self.books:
            genres[book["genre"]] = genres.get(book["genre"], 0) + 1
            authors[book["author"]] = authors.get(book["author"], 0) + 1
        
        most_common_genre = max(genres, key=genres.get) if genres else "Нет"
        most_read_author = max(authors, key=authors.get) if authors else "Нет"
        
        stats_text = f"""
📊 СТАТИСТИКА ПРОЧИТАННЫХ КНИГ
{'='*35}

📚 Всего книг: {total_books}
📖 Всего страниц: {total_pages}
📏 Средняя длина: {avg_pages} стр.

🏆 Самый популярный жанр: {most_common_genre} ({genres.get(most_common_genre, 0)} книг)
👤 Самый читаемый автор: {most_read_author} ({authors.get(most_read_author, 0)} книг)

📌 Распределение по жанрам:
"""
        for genre, count in sorted(genres.items(), key=lambda x: x[1], reverse=True):
            stats_text += f"   • {genre}: {count} книг\n"

        messagebox.showinfo("Статистика", stats_text)


if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()
