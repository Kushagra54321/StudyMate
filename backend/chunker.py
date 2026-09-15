# backend/chunking.py

from pathlib import Path

from pdf_reader import extract_text_from_pdf


def create_chunks(pages, chunk_size=500, overlap=100):
    """
    PDF ke pages ke text ko smaller chunks mein divide karta hai.

    Parameters:
        pages: pdf_reader.py se extracted pages
        chunk_size: ek chunk mein maximum characters
        overlap: next chunk mein previous chunk ke kitne characters repeat honge

    Return:
        [
            {
                "chunk_id": "page_1_chunk_1",
                "page_number": 1,
                "text": "Chunk ka text..."
            }
        ]
    """

    all_chunks = []

    for page in pages:
        page_number = page["page_number"]
        text = page["text"]

        start = 0
        chunk_number = 1

        while start < len(text):
            end = start + chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:
                all_chunks.append(
                    {
                        "chunk_id": f"page_{page_number}_chunk_{chunk_number}",
                        "page_number": page_number,
                        "text": chunk_text,
                    }
                )

            # Next chunk overlap ke saath start hoga
            start = end - overlap
            chunk_number += 1

    return all_chunks


def display_chunks(chunks):
    """
    Terminal mein chunks ko readable format mein print karta hai.
    """

    print("\n")
    print("#" * 80)
    print(f"TOTAL CHUNKS CREATED: {len(chunks)}")
    print("#" * 80)

    for index, chunk in enumerate(chunks, start=1):
        print("\n" + "=" * 80)
        print(f"CHUNK {index}")
        print(f"Chunk ID    : {chunk['chunk_id']}")
        print(f"Page Number : {chunk['page_number']}")
        print(f"Characters  : {len(chunk['text'])}")
        print("-" * 80)
        print(chunk["text"])
        print("=" * 80)


if __name__ == "__main__":
    # PDF ka path
    pdf_path = Path(__file__).resolve().parent.parent / "data" / "sample.pdf"

    print("Reading PDF...")

    # Step 1: PDF se pages ka text extract
    pages = extract_text_from_pdf(pdf_path)

    print(f"PDF se {len(pages)} pages ka text extract hua.")

    # Step 2: Pages ke text ko chunks mein convert
    chunks = create_chunks(
        pages=pages,
        chunk_size=500,
        overlap=100
    )

    # Step 3: Chunks terminal mein show
    display_chunks(chunks)