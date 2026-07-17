import re


class Detector:

    def __init__(self):

        self.email_pattern = re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        )

    def detect(self, text):

        matches = []

        for match in self.email_pattern.finditer(text):

            matches.append({
                "type": "EMAIL",
                "value": match.group(),
                "start": match.start(),
                "end": match.end()
            })

        return matches