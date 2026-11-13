
from dataclasses import dataclass


class ZythonLexerError(Exception):
    pass


@dataclass
class Token:
    type: str
    value: object
    line: int
    column: int


KEYWORDS = {
    "fn", "let", "return",
    "if", "else", "while",
    "for", "in", "true",
    "false", "null", "end",
    "module", "class", "import"
}


class Lexer:

    def __init__(self, source):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def peek(self, offset=0):
        pos = self.position + offset
        if pos >= len(self.source):
            return "\0"
        return self.source[pos]

    def advance(self):
        char = self.peek()
        self.position += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def add_token(self, kind, value, line, column):
        self.tokens.append(
            Token(kind, value, line, column)
        )

    def tokenize(self):

        while self.peek() != "\0":

            char = self.peek()

            if char in " \t\r":
                self.advance()
                continue

            if char == "\n":
                line = self.line
                self.advance()
                self.add_token(
                    "NEWLINE", "\n", line, 1
                )
                continue

            if char == "#":
                while self.peek() not in ("\n", "\0"):
                    self.advance()
                continue

            line = self.line
            column = self.column

            if char.isdigit():
                self.number(line, column)
                continue

            if char.isalpha() or char == "_":
                self.identifier(line, column)
                continue

            if char in "\"'":
                self.string(line, column)
                continue

            operators = {
                "+", "-", "*", "/", "%",
                "=", "!", "<", ">", "(",
                ")", "[", "]", "{", "}",
                ",", ".", ":"
            }

            if char in operators:
                self.advance()
                self.add_token(
                    "OPERATOR", char, line, column
                )
                continue

            raise ZythonLexerError(
                f"{line}:{column}: Invalid character {char}"
            )

        self.add_token(
            "EOF", None, self.line, self.column
        )

        return self.tokens

    def number(self, line, column):
        value = ""

        while self.peek().isdigit():
            value += self.advance()

        if self.peek() == "." and self.peek(1).isdigit():
            value += self.advance()

            while self.peek().isdigit():
                value += self.advance()

            value = float(value)
        else:
            value = int(value)

        self.add_token("NUMBER", value, line, column)

    def identifier(self, line, column):
        value = ""

        while self.peek().isalnum() or self.peek() == "_":
            value += self.advance()

        kind = (
            "KEYWORD"
            if value in KEYWORDS
            else "IDENTIFIER"
        )

        self.add_token(kind, value, line, column)

    def string(self, line, column):
        quote = self.advance()
        value = ""

        while self.peek() not in (quote, "\0"):
            char = self.advance()

            if char == "\\":
                escaped = self.advance()

                mapping = {
                    "n": "\n",
                    "t": "\t",
                    "r": "\r",
                    "\\": "\\",
                    '"': '"',
                    "'": "'"
                }

                if escaped not in mapping:
                    raise ZythonLexerError(
                        f"{line}:{column}: Invalid escape"
                    )

                value += mapping[escaped]
            else:
                value += char

        if self.peek() == "\0":
            raise ZythonLexerError(
                f"{line}:{column}: Unterminated string"
            )

        self.advance()

        self.add_token(
            "STRING", value, line, column
        )
