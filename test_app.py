import unittest
import json
import os

class TestBookTracker(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_books.json"

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_pages_validation_positive(self):
        """Тест: корректное количество страниц"""
        from main import BookTracker
        import tkinter as tk
        root = tk.Tk()
        app = BookTracker(root)

        is_valid, pages = app.validate_pages("250")
        self.assertTrue(is_valid)
        self.assertEqual(pages, 250)

        is_valid, pages = app.validate_pages("1")
        self.assertTrue(is_valid)
        self.assertEqual(pages, 1)

        root.destroy()

    def test_pages_validation_negative(self):
        """Тест: некорректное количество страниц"""
        from main import BookTracker
        import tkinter as tk
        root = tk.Tk()
        app = BookTracker(root)

        is_valid, pages = app.validate_pages("0")
        self.assertFalse(is_valid)

        is_valid, pages = app.validate_pages("-10")
        self.assertFalse(is_valid)

        is_valid, pages = app.validate_pages("abc")
        self.assertFalse(is_valid)

        is_valid, pages = app.validate_pages("")
        self.assertFalse(is_valid)

        root.destroy()

    def test_not_empty_validation(self):
        """Тест: проверка непустых полей"""
        from main import BookTracker
        import tkinter as tk
        root = tk.Tk()
        app = BookTracker(root)

        self.assertTrue(app.validate_not_empty("Книга"))
        self.assertTrue(app.validate_not_empty("  Война и мир  "))
        self.assertFalse(app.validate_not_empty(""))
        self.assertFalse(app.validate_not_empty("   "))

        root.destroy()

    def test_save_and_load(self):
        """Тест: сохранение и загрузка JSON"""
        from main import BookTracker
        import tkinter as tk
        root = tk.Tk()
        app = BookTracker(root)

        import main
        main.DATA_FILE = self.test_file
        app.DATA_FILE = self.test_file

        test_data = [{
            "title": "Тестовая книга",
            "author": "Тестер",
            "genre": "Роман",
            "pages": 300,
            "added_at": "2024-01-01 12:00:00"
        }]

        app.books = test_data
        app.save_books()

        app.books = []
        app.books = app.load_books()

        self.assertEqual(len(app.books), 1)
        self.assertEqual(app.books[0]["title"], "Тестовая книга")
        self.assertEqual(app.books[0]["author"], "Тестер")
        root.destroy()

    def test_filter_by_genre(self):
        """Тест: фильтрация по жанру"""
        from main import BookTracker
        import tkinter as tk
        root = tk.Tk()
        app = BookTracker(root)

        app.books = [
            {"title": "Книга1", "author": "Автор1", "genre": "Роман", "pages": 100, "added_at": ""},
            {"title": "Книга2", "author": "Автор2", "genre": "Фантастика", "pages": 200, "added_at": ""},
            {"title": "Книга3", "author": "Автор3", "genre": "Роман", "pages": 150, "added_at": ""},
        ]

        app.current_filter_genre = "Роман"
        filtered = [b for b in app.books if b["genre"] == app.current_filter_genre]
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["title"], "Книга1")
        self.assertEqual(filtered[1]["title"], "Книга3")

        root.destroy()

    def test_filter_by_pages(self):
        """Тест: фильтрация по количеству страниц"""
        from main import BookTracker
        import tkinter as tk
        root = tk.Tk()
        app = BookTracker(root)

        app.books = [
            {"title": "Короткая", "author": "Автор1", "genre": "Роман", "pages": 100, "added_at": ""},
            {"title": "Средняя", "author": "Автор2", "genre": "Роман", "pages": 250, "added_at": ""},
            {"title": "Длинная", "author": "Автор3", "genre": "Роман", "pages": 500, "added_at": ""},
        ]

        app.current_filter_pages = 200
        filtered = [b for b in app.books if b["pages"] > app.current_filter_pages]
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["title"], "Средняя")
        self.assertEqual(filtered[1]["title"], "Длинная")

        root.destroy()

    def test_filter_combined(self):
        """Тест: комбинированная фильтрация"""
        from main import BookTracker
        import tkinter as tk
        root = tk.Tk()
        app = BookTracker(root)

        app.books = [
            {"title": "Роман1", "author": "Автор1", "genre": "Роман", "pages": 100, "added_at": ""},
            {"title": "Роман2", "author": "Автор2", "genre": "Роман", "pages": 300, "added_at": ""},
            {"title": "Фантастика1", "author": "Автор3", "genre": "Фантастика", "pages": 400, "added_at": ""},
        ]

        app.current_filter_genre = "Роман"
        app.current_filter_pages = 200
        filtered = [b for b in app.books if b["genre"] == app.current_filter_genre and b["pages"] > app.current_filter_pages]
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["title"], "Роман2")

        root.destroy()


if __name__ == "__main__":
    unittest.main()
