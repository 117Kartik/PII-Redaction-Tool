from collections import Counter
from datetime import datetime


class Report:

    def __init__(self):

        self.counter = Counter()

        self.paragraphs = 0

    def add(self, matches):

        for match in matches:
            self.counter[match["type"]] += 1

    def set_paragraph_count(self, count):

        self.paragraphs = count

    def save(self, path, input_file, output_file):

        total = sum(self.counter.values())

        with open(path, "w", encoding="utf-8") as f:

            f.write("=" * 60 + "\n")
            f.write("PII DETECTION & REDACTION REPORT\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Generated On : {datetime.now()}\n")
            f.write(f"Input File   : {input_file}\n")
            f.write(f"Output File  : {output_file}\n")
            f.write(f"Paragraphs   : {self.paragraphs}\n\n")

            f.write("Detected Entities\n")
            f.write("-" * 60 + "\n")

            for entity in sorted(self.counter):

                f.write(f"{entity:<20}{self.counter[entity]}\n")

            f.write("-" * 60 + "\n")

            f.write(f"TOTAL DETECTIONS : {total}\n\n")

            f.write("Evaluation Approach\n")
            f.write("-" * 60 + "\n")

            f.write(
                "The generated report summarizes the detected entity "
                "counts for the processed document. "
                "Precision, Recall and F1-score require a manually "
                "annotated ground-truth dataset and therefore are "
                "not automatically calculated in the current version.\n"
            )

            f.write("\n")
            f.write("=" * 60 + "\n")
            f.write("Processing Completed Successfully\n")
            f.write("=" * 60 + "\n")