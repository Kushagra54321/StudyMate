# backend/pdf_reader.py

import fitz
from pathlib import Path


def extract_text_from_pdf(pdf_path: str):
    """
    PDF se text extract karta hai.

    Return format:
    [
        {
            "page_number": 1,
            "text": "Page 1 ka complete text..."
        },
        {
            "page_number": 2,
            "text": "Page 2 ka complete text..."
        }
    ]
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file nahi mili: {pdf_path}")

    document = fitz.open(pdf_path)

    pages = []

    for page_index, page in enumerate(document):
        page_text = page.get_text("text").strip()

        if page_text:
            pages.append(
                {
                    "page_number": page_index + 1,
                    "text": page_text,
                }
            )

    document.close()

    return pages


if __name__ == "__main__":
    pdf_path = "../data/StudyMate_Computer_Fundamentals_Sample.pdf"

    pages = extract_text_from_pdf(pdf_path)

    print(f"\nTotal pages extracted: {len(pages)}\n")

    for page in pages:
        print("=" * 70)
        print(f"PAGE {page['page_number']}")
        print("=" * 70)
        print(page["text"][:500])
        print()