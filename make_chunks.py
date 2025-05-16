import pickle
from pathlib import Path
from PyPDF2 import PdfReader

# Path to your PDF file
pdf_path = Path("ACFR2024.pdf")
reader = PdfReader(str(pdf_path))

# Chunk text from PDF pages
chunks = []
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    if text:
        for para in text.split("\n\n"):
            clean_para = para.strip().replace("\n", " ")
            if len(clean_para) > 100:
                chunks.append({"page": i+1, "content": clean_para})

# Save chunks to .pkl
with open("trs_acfr2024_chunks.pkl", "wb") as f:
    pickle.dump(chunks, f)

print(f"✅ Created trs_acfr2024_chunks.pkl with {len(chunks)} chunks.")
