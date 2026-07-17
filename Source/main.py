from pathlib import Path

from docx import Document

from detector import Detector
from replacer import Replacer
from document_traversal import traverse_document


# Project Paths
BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "IP" / "Red Herring Prospectus.docx"

OUTPUT_DIR = BASE_DIR / "OP"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "Red_Herring_Prospectus_Redacted.docx"


# Debug Configuration
DEBUG = True
LIMIT = 50


# Load Document
doc = Document(str(INPUT_FILE))

# Initialize Components
detector = Detector()
replacer = Replacer()


count = 0

for paragraph in traverse_document(doc):

    count += 1

    # Process only a few paragraphs while debugging
    if DEBUG and count > LIMIT:
        break

    matches = detector.detect(paragraph.text)

    if not matches:
        continue

    print("-" * 60)
    print(f"Paragraph {count}")
    print(paragraph.text)

    replacer.replace_in_paragraph(paragraph, matches)


# Save the modified document
doc.save(str(OUTPUT_FILE))

print("\nDone!")
print(f"Processed {count} paragraphs.")
print(f"Redacted document saved to:\n{OUTPUT_FILE}")