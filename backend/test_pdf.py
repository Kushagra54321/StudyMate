from pdf_reader import extract_text_from_pdf
from chunker import create_chunks

# 1. PDF se text nikalo
pages = extract_text_from_pdf("../data/sample.pdf")

# 2. Text ke chunks banao (500 characters per chunk)
chunks = create_chunks(pages, chunk_size=500)

# 3. Test output print karo
print(f"Total Chunks Created: {len(chunks)}\n")

# Shuruat ke 2 chunks check karo
for i, chunk in enumerate(chunks[:2]):
    print(f"--- CHUNK {i+1} (Page {chunk['page']}) ---")
    print(chunk['text'])
    print("-" * 30)