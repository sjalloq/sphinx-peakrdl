from typing import List
import os
import re

from docutils import nodes
from docutils.utils import new_document

from .md_parsers import MD_DOCUTILS, MD_HTML


def rdlfc_to_markdown(text: str) -> str:
    """Convert RDL Format Code tags to Markdown equivalents.

    Handles the subset of RDLFormatCode tags that have natural Markdown
    representations.  Tags with no Markdown equivalent (e.g. [color], [size])
    are stripped.
    """
    replacements = [
        # Inline formatting
        (r'\[b\](.*?)\[/b\]', r'**\1**'),
        (r'\[i\](.*?)\[/i\]', r'*\1*'),
        (r'\[u\](.*?)\[/u\]', r'<u>\1</u>'),
        (r'\[code\](.*?)\[/code\]', r'`\1`'),

        # Links
        (r'\[url=([^\]]+)\](.*?)\[/url\]', r'[\2](\1)'),
        (r'\[url\](.*?)\[/url\]', r'<\1>'),
        (r'\[email\](.*?)\[/email\]', r'<mailto:\1>'),

        # Images
        (r'\[img\](.*?)\[/img\]', r'![](\1)'),

        # Block-level
        (r'\[br\]', '  \n'),
        (r'\[p\]', '\n\n'),
        (r'\[/p\]', '\n\n'),

        # Escapes and whitespace
        (r'\[lb\]', '['),
        (r'\[rb\]', ']'),
        (r'\[sp\]', '\u00a0'),
        (r'\[quote\]', '"'),
        (r'\[/quote\]', '"'),

        # Strip tags with no Markdown equivalent
        (r'\[color=[^\]]+\]', ''),
        (r'\[/color\]', ''),
        (r'\[size=[^\]]+\]', ''),
        (r'\[/size\]', ''),
    ]

    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text, flags=re.DOTALL)

    # Convert [list]/[*]/[/list] to Markdown bullet lists
    text = _convert_lists(text)

    return text


def _convert_lists(text: str) -> str:
    """Convert RDL [list]/[*]/[/list] tags to Markdown lists."""
    # Remove [list] and [/list] tags, adding paragraph breaks
    text = re.sub(r'\[list(?:=[^\]]+)?\]', '\n', text)
    text = re.sub(r'\[/list\]', '\n', text)
    # Convert [*] bullets to Markdown list items
    text = re.sub(r'\[\*\]\s*', '\n- ', text)
    return text


def render_to_docutils(md_string: str, src_path: str, src_line_offset: int = 0) -> List[nodes.Element]:
    MD_DOCUTILS.options["document"] = new_document(src_path)

    env = {
        "relative-images": os.path.dirname(src_path)
    }

    md_string = rdlfc_to_markdown(md_string)
    doc = MD_DOCUTILS.render(md_string, env)
    assert isinstance(doc, nodes.document)

    if src_line_offset != 0:
        for node in doc.traverse(nodes.Element):
            if node.line is not None:
                node.line += src_line_offset

    # MyST renderer will produce a top-level document.
    # Return the children so that they can be grafted into an existing document
    return doc.children


def render_to_html(md_string: str) -> str:
    doc = MD_HTML.render(md_string)
    return doc
