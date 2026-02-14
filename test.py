import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import sqlite3
import json
import markdown2
from tkhtmlview import HTMLLabel
from pygments import highlight
from pygments.lexers import guess_lexer, PythonLexer
from pygments.formatters import HtmlFormatter

DB_FILE = "notebook.db"

# =========================
# دیتابیس
# =========================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            title TEXT,
            description_md TEXT,
            code TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )
    ''')
    conn.commit()
    conn.close()

# =========================
# برنامه اصلی
# =========================
class MarkdownNotebookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Unreal Engine Note")
        self.root.geometry("1000x650")
        self.root.iconbitmap('icon.ico')

        init_db()
        self.conn = sqlite3.connect(DB_FILE)
        self.projects = {}  # project_name: id
        self.note_frames = {}  # project_name: frame_widget
        self.current_project = None
        self.dark_mode = False

        # سمت چپ: پروژه‌ها
        left_frame = tk.Frame(root, width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(left_frame, text="Projects", font=("Arial", 14, "bold")).pack(pady=5)
        self.project_listbox = tk.Listbox(left_frame)
        self.project_listbox.pack(fill=tk.Y, expand=True)
        self.project_listbox.bind("<<ListboxSelect>>", self.select_project)

        tk.Button(left_frame, text="New Project", command=self.add_project).pack(pady=5)
        tk.Button(left_frame, text="Darl/Light Mode", command=self.toggle_theme).pack(pady=5)
        tk.Button(left_frame, text="Saves As Json", command=self.export_json).pack(pady=2)
        tk.Button(left_frame, text="Load Json", command=self.import_json).pack(pady=2)

        # سمت راست: تب پروژه‌ها
        right_frame = tk.Frame(root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.tabs = ttk.Notebook(right_frame)
        self.tabs.pack(fill=tk.BOTH, expand=True)

        self.load_projects_from_db()

    # =========================
    # انتخاب پروژه
    # =========================
    def select_project(self, event):
        if not self.project_listbox.curselection():
            return
        index = self.project_listbox.curselection()[0]
        project_name = self.project_listbox.get(index)
        self.current_project = project_name
        for i in range(len(self.tabs.tabs())):
            if self.tabs.tab(i, "text") == project_name:
                self.tabs.select(i)
                break

    # =========================
    # پروژه‌ها
    # =========================
    def load_projects_from_db(self):
        c = self.conn.cursor()
        c.execute("SELECT id, name FROM projects")
        for pid, name in c.fetchall():
            self.projects[name] = pid
            self.project_listbox.insert(tk.END, name)
            self.create_project_tab(name)

    def add_project(self):
        name = simpledialog.askstring("New Project", "Enter Name Project:")
        if not name:
            return
        if name in self.projects:
            messagebox.showwarning("Warning", "The Project Has Created, Please Make Sure!")
            return
        c = self.conn.cursor()
        c.execute("INSERT INTO projects (name) VALUES (?)", (name,))
        self.conn.commit()
        pid = c.lastrowid
        self.projects[name] = pid
        self.project_listbox.insert(tk.END, name)
        self.create_project_tab(name)

    # =========================
    # ایجاد تب پروژه
    # =========================
    def create_project_tab(self, project_name):
        frame = tk.Frame(self.tabs)
        self.tabs.add(frame, text=project_name)
        self.note_frames[project_name] = frame

        # جستجو
        tk.Label(frame, text="Search:", font=("Arial", 12)).pack(anchor="w")
        search_entry = tk.Entry(frame)
        search_entry.pack(fill=tk.X)
        search_entry.bind("<KeyRelease>", lambda e, p=project_name: self.search_notes(p, search_entry.get()))

        # لیست یادداشت‌ها
        listbox = tk.Listbox(frame)
        listbox.pack(fill=tk.Y, side=tk.LEFT, padx=5, pady=5)
        listbox.bind("<<ListboxSelect>>", lambda e, p=project_name: self.show_note(p))

        # بخش محتوا
        content_frame = tk.Frame(frame)
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(content_frame, text="Title:").pack(anchor="w")
        title_entry = tk.Entry(content_frame, font=("Arial", 14))
        title_entry.pack(fill=tk.X)

        tk.Label(content_frame, text="Summary And Code:").pack(anchor="w")
        text_widget = tk.Text(content_frame, wrap="word")
        text_widget.pack(fill=tk.BOTH, expand=True)
        # Live Preview
        text_widget.bind("<KeyRelease>", lambda e, p=project_name: self.render_note(p))

        tk.Label(content_frame, text="Preview:").pack(anchor="w")
        html_label = HTMLLabel(content_frame, html="", background="white")
        html_label.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(content_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame, text="Save/Edit Summary",
                  command=lambda p=project_name: self.add_note(p)).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Display Markdown",
                  command=lambda p=project_name: self.render_note(p)).pack(side=tk.LEFT)

        frame.widgets = {
            "listbox": listbox,
            "title_entry": title_entry,
            "text_widget": text_widget,
            "html_label": html_label,
            "search_entry": search_entry
        }

        self.load_notes_from_db(project_name)

    # =========================
    # یادداشت‌ها
    # =========================
    def load_notes_from_db(self, project_name):
        pid = self.projects[project_name]
        c = self.conn.cursor()
        c.execute("SELECT title FROM notes WHERE project_id=?", (pid,))
        frame = self.note_frames[project_name]
        listbox = frame.widgets["listbox"]
        listbox.delete(0, tk.END)
        for (title,) in c.fetchall():
            listbox.insert(tk.END, title)

    def add_note(self, project_name):
        frame = self.note_frames[project_name]
        title = frame.widgets["title_entry"].get().strip()
        if not title:
            messagebox.showwarning("Warning", "Title Is Empty!")
            return
        content = frame.widgets["text_widget"].get("1.0", tk.END).strip()
        parts = content.split("```")
        desc_md = parts[0].strip()
        code = parts[1].strip() if len(parts) > 1 else ""
        pid = self.projects[project_name]
        c = self.conn.cursor()
        c.execute("SELECT id FROM notes WHERE project_id=? AND title=?", (pid, title))
        result = c.fetchone()
        if result:
            note_id = result[0]
            c.execute("UPDATE notes SET description_md=?, code=? WHERE id=?", (desc_md, code, note_id))
        else:
            c.execute("INSERT INTO notes (project_id, title, description_md, code) VALUES (?, ?, ?, ?)",
                      (pid, title, desc_md, code))
        self.conn.commit()
        self.load_notes_from_db(project_name)

    def show_note(self, project_name):
        frame = self.note_frames[project_name]
        listbox = frame.widgets["listbox"]
        if not listbox.curselection():
            return
        index = listbox.curselection()[0]
        title = listbox.get(index)
        pid = self.projects[project_name]
        c = self.conn.cursor()
        c.execute("SELECT description_md, code FROM notes WHERE project_id=? AND title=?", (pid, title))
        result = c.fetchone()
        if result:
            desc_md, code = result
            frame.widgets["title_entry"].delete(0, tk.END)
            frame.widgets["title_entry"].insert(0, title)
            combined = desc_md + ("\n```" + code + "```" if code else "")
            frame.widgets["text_widget"].delete("1.0", tk.END)
            frame.widgets["text_widget"].insert(tk.END, combined)
            self.render_note(project_name)

    # =========================
    # رندر Markdown + هایلایت کد
    # =========================
    def render_note(self, project_name):
        frame = self.note_frames[project_name]
        content = frame.widgets["text_widget"].get("1.0", tk.END).strip()
        parts = content.split("```")
        desc_md = parts[0]
        code = parts[1] if len(parts) > 1 else ""
        html = markdown2.markdown(desc_md)
        if code:
            try:
                lexer = guess_lexer(code)
            except:
                lexer = PythonLexer()
            style = "monokai" if self.dark_mode else "friendly"
            formatter = HtmlFormatter(style=style, noclasses=True)
            highlighted = highlight(code, lexer, formatter)
            html += "<h5>Script:</h5>" + highlighted
        bg = "black" if self.dark_mode else "white"
        fg = "white" if self.dark_mode else "black"
        html = f"<body style='background-color:{bg}; color:{fg}'>{html}</body>"
        frame.widgets["html_label"].set_html(html)

    # =========================
    # جستجو
    # =========================
    def search_notes(self, project_name, query):
        frame = self.note_frames[project_name]
        listbox = frame.widgets["listbox"]
        listbox.delete(0, tk.END)
        pid = self.projects[project_name]
        c = self.conn.cursor()
        c.execute("SELECT title FROM notes WHERE project_id=?", (pid,))
        for (title,) in c.fetchall():
            if query.lower() in title.lower():
                listbox.insert(tk.END, title)

    # =========================
    # دارک مود
    # =========================
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        for frame in self.note_frames.values():
            frame.widgets["text_widget"].configure(
                bg="black" if self.dark_mode else "white",
                fg="white" if self.dark_mode else "black",
                insertbackground="white" if self.dark_mode else "black"
            )
            frame.widgets["html_label"].configure(background="black" if self.dark_mode else "white")
        self.render_note(self.current_project or list(self.note_frames.keys())[0])

    # =========================
    # JSON Export/Import
    # =========================
    def export_json(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files","*.json")])
        if file_path:
            data = {}
            c = self.conn.cursor()
            for name, pid in self.projects.items():
                c.execute("SELECT title, description_md, code FROM notes WHERE project_id=?", (pid,))
                data[name] = [{"title": t, "description_md": d, "code": co} for t, d, co in c.fetchall()]
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Successful", "Imported!")

    def import_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files","*.json")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            c = self.conn.cursor()
            for project_name, notes in data.items():
                if project_name not in self.projects:
                    c.execute("INSERT INTO projects (name) VALUES (?)", (project_name,))
                    pid = c.lastrowid
                    self.projects[project_name] = pid
                    self.project_listbox.insert(tk.END, project_name)
                    self.create_project_tab(project_name)
                else:
                    pid = self.projects[project_name]
                for note in notes:
                    c.execute("SELECT id FROM notes WHERE project_id=? AND title=?", (pid, note["title"]))
                    if not c.fetchone():
                        c.execute("INSERT INTO notes (project_id, title, description_md, code) VALUES (?, ?, ?, ?)",
                                  (pid, note["title"], note["description_md"], note["code"]))
            self.conn.commit()
            for project_name in self.projects:
                self.load_notes_from_db(project_name)
            messagebox.showinfo("Successful", "Imported!")

# =========================
# اجرا
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownNotebookApp(root)
    root.mainloop()
