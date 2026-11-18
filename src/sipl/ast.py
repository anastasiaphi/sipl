from dataclasses import dataclass


@dataclass
class Span:
    """Позиція у тексті програми """
    line: int
    column: int
    end_line: int
    end_column: int

    def __str__(self):
        return f"рядок {self.line}, колонка {self.column}"


class Node:
    """Спільний батьківський клас для всіх вузлів AST"""
    pass

@dataclass
class Num(Node):
    """Число: n"""
    value: int
    span: Span = None


@dataclass
class Var(Node):
    """Змінна: x"""
    name: str
    span: Span = None


@dataclass
class BinOp(Node):
    """Арифметична операція: a1 + a2, a1 - a2, a1 * a2"""
    op: str
    left: Node
    right: Node
    span: Span = None

@dataclass
class Compare(Node):
    """Порівняння: a1 = a2, a1 > a2"""
    op: str
    left: Node
    right: Node
    span: Span = None


@dataclass
class Or(Node):
    """Диз'юнкція: b1 ∨ b2"""
    left: Node
    right: Node
    span: Span = None


@dataclass
class Not(Node):
    """Заперечення: ¬b"""
    cond: Node
    span: Span = None

@dataclass
class Assign(Node):
    """Присвоєння: x := a"""
    name: str
    expr: Node
    span: Span = None


@dataclass
class Seq(Node):
    """Послідовне виконання: S1 ; S2"""
    first: Node
    second: Node
    span: Span = None


@dataclass
class If(Node):
    """Розгалуження: if b then S1 else S2"""
    cond: Node
    then_branch: Node
    else_branch: Node
    span: Span = None


@dataclass
class While(Node):
    """Цикл: while b do S"""
    cond: Node
    body: Node
    span: Span = None


@dataclass
class Block(Node):
    """Блок: begin S end"""
    body: Node
    span: Span = None


@dataclass
class Skip(Node):
    """Порожній оператор: skip"""
    span: Span = None

@dataclass
class Program(Node):
    """Програма: begin S end"""
    body: Node
    span: Span = None

def show_tree(node, level=0, with_spans=False):
    """Повертає AST у вигляді дерева з відступами """
    indent = "  " * level
    line = indent + type(node).__name__
    children = []

    for field_name, value in vars(node).items():
        if field_name == "span":
            continue
        if isinstance(value, Node):
            children.append(value)
        else:
            line += " " + str(value)

    if with_spans and node.span is not None:
        line += f"    [{node.span}]"

    result = line + "\n"
    for child in children:
        result += show_tree(child, level + 1, with_spans)
    return result