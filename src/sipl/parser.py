from pathlib import Path

from lark import Lark
from lark.exceptions import UnexpectedInput, UnexpectedCharacters, UnexpectedToken

from sipl.ast import (
    Span, Program, Assign, Seq, If, While, Block, Skip,
    Num, Var, BinOp, Compare, Or, Not,
)

GRAMMAR_FILE = Path(__file__).parent / "sipl.lark"

lark_parser = Lark.open(
    str(GRAMMAR_FILE),
    start="program",
    parser="lalr",
    propagate_positions=True,
)

class SiplSyntaxError(Exception):
    """Синтаксична помилка в програмі SIPL."""

    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Синтаксична помилка (рядок {line}, колонка {column}): {message}")


def parse(text):
    """Розбирає текст програми SIPL і повертає AST """
    try:
        tree = lark_parser.parse(text)
    except UnexpectedInput as error:
        raise make_syntax_error(error, text) from None
    return convert(tree)


def parse_file(path):
    """Читає програму з файлу і розбирає її"""
    text = Path(path).read_text(encoding="utf-8")
    return parse(text)


def make_span(tree):
    """Позиція вузла з дерева Lark"""
    meta = tree.meta
    if meta.empty:
        return None
    return Span(meta.line, meta.column, meta.end_line, meta.end_column)


def convert(tree):
    """Рекурсивне перетворення вузла дерева Lark на вузол AST"""
    kind = tree.data
    children = tree.children
    span = make_span(tree)

    if kind == "program":
        return Program(convert(children[0]), span)
    elif kind == "seq":
        return Seq(convert(children[0]), convert(children[1]), span)
    elif kind == "assign":
        name = str(children[0])
        return Assign(name, convert(children[1]), span)
    elif kind == "if_stmt":
        return If(convert(children[0]), convert(children[1]), convert(children[2]), span)
    elif kind == "while_stmt":
        return While(convert(children[0]), convert(children[1]), span)
    elif kind == "block":
        return Block(convert(children[0]), span)
    elif kind == "skip":
        return Skip(span)


    elif kind == "num":
        return Num(int(children[0]), span)
    elif kind == "var":
        return Var(str(children[0]), span)
    elif kind == "add":
        return BinOp("+", convert(children[0]), convert(children[1]), span)
    elif kind == "sub":
        return BinOp("-", convert(children[0]), convert(children[1]), span)
    elif kind == "mult":
        return BinOp("*", convert(children[0]), convert(children[1]), span)

    elif kind == "eq":
        return Compare("=", convert(children[0]), convert(children[1]), span)
    elif kind == "gr":
        return Compare(">", convert(children[0]), convert(children[1]), span)
    elif kind == "or_cond":
        return Or(convert(children[0]), convert(children[1]), span)
    elif kind == "neg":
        return Not(convert(children[0]), span)

    else:
        raise ValueError("Невідомий вузол дерева: " + str(kind))

def token_to_text(name):
    """Перетворення на зрозумілий текст (';')"""
    if name == "VAR":
        return "змінна"
    if name == "NUMBER":
        return "число"
    terminal = lark_parser.get_terminal(name)
    return "'" + terminal.pattern.value + "'"


def make_syntax_error(error, text):
    """Підомлення про синтаксичну помилку"""
    line = error.line
    column = error.column

    if isinstance(error, UnexpectedCharacters):
        symbol = text[error.pos_in_stream]
        message = f"незрозумілий символ '{symbol}'"
        expected = error.allowed
    elif isinstance(error, UnexpectedToken):
        if error.token.type == "$END":
            message = "програма несподівано закінчилась"
        else:
            message = f"неочікуване '{error.token}'"
        expected = error.expected
    else:
        message = "помилка розбору"
        expected = set()

    if expected:
        names = sorted(token_to_text(name) for name in expected)
        message += ", очікувалось: " + ", ".join(names)

    return SiplSyntaxError(message, line, column)

