from docx.document import Document as DocumentObject
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P


def iter_block_items(parent):

    if isinstance(parent, DocumentObject):
        parent_element = parent.element.body

    elif isinstance(parent, _Cell):
        parent_element = parent._tc

    else:
        raise TypeError(f"Unsupported parent type: {type(parent)}")

    for child in parent_element.iterchildren():

        if isinstance(child, CT_P):
            yield Paragraph(child, parent)

        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def traverse_document(parent, visited=None):

    if visited is None:
        visited = set()

    for block in iter_block_items(parent):

        if isinstance(block, Paragraph):

            # Skip duplicate paragraph objects
            if id(block) in visited:
                continue

            visited.add(id(block))
            yield block

        elif isinstance(block, Table):

            for row in block.rows:

                for cell in row.cells:

                    yield from traverse_document(cell, visited)