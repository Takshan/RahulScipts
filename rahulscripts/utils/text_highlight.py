from typing import Union

from rich.highlighter import Highlighter
from rich.text import Text


class SequenceHighlighter(Highlighter):
    """Highlight fasta sequence

    :param Highlighter: _description_
    :type Highlighter: _type_
    """

    def __init__(self):
        self.constant = ["CAGTA", "GTCAT", "TACTG", "ATGAC"]

    def highlight(self, text, strict=False):
        if str(text).strip().isalpha() and str(text)[8:13] in self.constant:
            text.stylize("color(10)", 0, 8)
            if strict:
                if str(text)[8:13] in self.constant:
                    text.stylize("color(13)", 8, 13)
                if str(text)[-9:-1] in self.constant:
                    text.stylize("color(10)", -9, -1)
                if str(text)[-14:-1] in self.constant:
                    text.stylize("color(13)", -14, -9)
            else:
                text.stylize("color(13)", 8, 13)
                text.stylize("color(10)", -9, -1)
                text.stylize("color(13)", -14, -9)
        return text

    def __call__(self, text: Union[str, Text], strict=False) -> Text:
        """Highlight a str or Text instance.

        Args:
            text (Union[str, ~Text]): Text to highlight.

        Raises:
            TypeError: If not called with text or str.

        Returns:
            Text: A test instance with highlighting applied.
        """
        if isinstance(text, str):
            highlight_text = Text(text)
        elif isinstance(text, Text):
            highlight_text = text.copy()
        else:
            raise TypeError(f"str or Text instance required, not {text!r}")
        self.highlight(highlight_text, strict=strict)
        return highlight_text
