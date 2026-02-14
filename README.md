# Markdown Notebook App

A desktop notebook application built with Python and Tkinter for organizing structured notes, Markdown content, and code snippets — all inside a clean project-based workspace.

This tool is designed for developers, learners, and anyone who wants a powerful technical note-taking environment.

---

## ✨ Features

- Project-based note organization  
- Markdown editor with live preview  
- Code block rendering with syntax highlighting  
- SQLite database storage  
- JSON import/export for portability  
- Note search functionality  
- Dark / Light UI themes  
- Desktop executable packaging  

---

## 🎯 Purpose

This application was created as a practical productivity tool for managing technical notes, tutorials, and code references in one place — especially useful for learning workflows and project documentation.

---

## 🧠 Development Notes

The core implementation of this application was generated with AI assistance.

Project structure, feature direction, customization, testing, and overall management were designed and supervised by the repository owner.

This reflects a modern workflow where AI accelerates development while human oversight drives architecture and usability.

---

## 🛠 Tech Stack

- Python  
- Tkinter GUI  
- SQLite database  
- Markdown rendering  
- Syntax highlighting  

---

## 📦 Installation

### 1 — Clone the repository

```bash
git clone https://github.com/yourusername/markdown-notebook.git
cd markdown-notebook
```

### 2 — Install dependencies

```bash
pip install markdown2 tkhtmlview pygments
```

---

## ▶ Running the App

```bash
python test.py
```

The SQLite database will be created automatically on first run.

---

## ⚙ Building an Executable

To build a standalone desktop executable:

```bash
pyinstaller --onefile --windowed --icon=icon.ico test.py
```

The compiled app will appear inside:

```
dist/
```

---

## 💾 Data Storage

- Notes are stored locally in SQLite  
- JSON export/import allows easy backup and migration  

---

## 🖼 Screenshots

Add screenshots of the app UI here.

Example:

```markdown
![Main UI](screenshots/main.png)
![Dark Mode](screenshots/dark.png)
```

Create a folder:

```
/screenshots
```

and place images inside it.

---

## 🚀 Use Cases

- Learning notes  
- Code snippets archive  
- Project documentation  
- Study notebook  
- Technical journaling  

---

## 🤝 Contribution

This project is intended for experimentation, learning, and personal productivity. Contributions and ideas are welcome.

---

## 📜 License

MIT License — feel free to use, modify, and expand.
