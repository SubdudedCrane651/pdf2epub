import os
import tkinter as tk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF
from ebooklib import epub

def pdf_to_epub_single_chapter(pdf_path, epub_path):
    doc = fitz.open(pdf_path)

    book = epub.EpubBook()
    book.set_identifier("pdf-conversion")
    book.set_title(os.path.basename(pdf_path))
    book.set_language("en")

    full_html = "<h1>{}</h1>".format(os.path.basename(pdf_path))

    image_counter = 1

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Extract text
        text = page.get_text("text")
        if text.strip():
            full_html += "<p>{}</p>".format(text.replace("\n", "<br>"))

        # Extract images
        for img in page.get_images(full=True):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)

            # Convert to PNG bytes
            if pix.n < 5:
                img_bytes = pix.tobytes("png")
            else:
                pix = fitz.Pixmap(fitz.csRGB, pix)
                img_bytes = pix.tobytes("png")

            img_name = f"image_{image_counter}.png"
            image_counter += 1

            epub_img = epub.EpubItem(
                uid=img_name,
                file_name=f"images/{img_name}",
                media_type="image/png",
                content=img_bytes
            )
            book.add_item(epub_img)

            full_html += f'<div><img src="images/{img_name}" /></div>'

    # Create one big chapter
    chapter = epub.EpubHtml(
        title="Content",
        file_name="content.xhtml",
        lang="en"
    )
    chapter.content = full_html
    book.add_item(chapter)

    # Navigation
    book.toc = (chapter,)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Basic CSS
    style = "body { font-family: Arial; } img { max-width: 100%; height: auto; }"
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=style
    )
    book.add_item(nav_css)

    # Spine
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
        pdf_to_epub_single_chapter(pdf_path, epub_path)
        messagebox.showinfo("Success", f"EPUB created:\n{epub_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# GUI
root = tk.Tk()
root.title("PDF to EPUB (Single Chapter + Images)")
root.geometry("350x150")

btn = tk.Button(root, text="Select PDF to Convert", command=select_pdf, height=2, width=25)
btn.pack(pady=40)

root.mainloop()