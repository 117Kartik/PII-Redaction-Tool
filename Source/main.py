from docx import Document

from detector import Detector
from document_traversal import traverse_document


doc = Document("IP/Red Herring Prospectus.docx")

detector = Detector()

LIMIT = 50

count = 0

for paragraph in traverse_document(doc):

    count += 1

    if count > LIMIT:
        break

    matches = detector.detect(paragraph.text)

    if matches:

        print("-" * 60)
        print(f"Paragraph {count}")
        print(paragraph.text)

        for match in matches:
            print(match)