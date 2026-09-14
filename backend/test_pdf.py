from pdf_reader import extract_text_from_pdf

pages = extract_text_from_pdf("../data/sample.pdf")

for page in pages:
    print("PAGE:", page["page"])
    print(page["text"][:500])