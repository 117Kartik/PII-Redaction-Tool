from pathlib import Path
import sys
from report import Report
from docx import Document

from detector import Detector
from replacer import Replacer
from document_traversal import traverse_document


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "IP" / "Red Herring Prospectus.docx"

OUTPUT_DIR = BASE_DIR / "OP"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "Red_Herring_Prospectus_Redacted.docx"


try:
    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()
except PermissionError:
    print("Please close the redacted document and run the program again.")
    sys.exit(1)


DEBUG = False
LIMIT = None


print(INPUT_FILE)
print(OUTPUT_FILE)


doc = Document(str(INPUT_FILE))

detector = Detector()
replacer = Replacer()
report = Report()


count = 0

for paragraph in traverse_document(doc):

    count += 1

    if LIMIT is not None and count > LIMIT:
        break

    matches = detector.detect(paragraph.text)
    report.add(matches)

    if not matches:
        continue

    # print("-" * 60)
    # print(f"Paragraph {count}")
    # print(paragraph.text)

    replacer.replace_in_paragraph(paragraph, matches)


doc.save(str(OUTPUT_FILE))
REPORT_FILE = OUTPUT_DIR / "Redaction_Report.txt"
report.set_paragraph_count(count)

report.save(
    REPORT_FILE,
    INPUT_FILE.name,
    OUTPUT_FILE.name
)

print("\nDone!")
print(f"Processed {count} paragraphs.")
print(f"Redacted document saved to:\n{OUTPUT_FILE}")
print(f"Report saved to:\n{REPORT_FILE}")