import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pdfminer.high_level import extract_text
from ebooklib import epub

def pdf_to_epub(pdf_path, epub_path):
    text = extract_text(pdf_path)

    book = epub.EpubBook()
    book.set_identifier("pdf-conversion")
    book.set_title(os.path.basename(pdf_path))
    book.set_language("en")

    chapter = epub.EpubHtml(title="Content", file_name="chap1.xhtml", lang="en")
    chapter.content = f"<h1>{os.path.basename(pdf_path)}</h1><pre>{text}</pre>"
    book.add_item(chapter)

    book.toc = (epub.Link("chap1.xhtml", "Content", "content"),)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    style = "body { font-family: Arial; white-space: pre-wrap; }"
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css",
                            media_type="text/css", content=style)
    book.add_item(nav_css)

    book.spine = ["nav", chapter]

    epub.write_epub(epub_path, book)


def select_pdf():
    pdf_path = filedialog.askopenfilename(
        title="Select PDF",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not pdf_path:
        return

    epub_path = os.path.splitext(pdf_path)[0] + ".epub"

    try:
        pdf_to_epub(pdf_path, epub_path)
        messagebox.showinfo("Success", f"EPUB created:\n{epub_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# GUI setup
root = tk.Tk()
root.title("PDF to EPUB Converter")
root.geometry("300x150")

btn = tk.Button(root, text="Select PDF to Convert", command=select_pdf, height=2, width=25)
btn.pack(pady=40)

root.mainloop()