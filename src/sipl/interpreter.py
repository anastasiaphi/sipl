from sipl.ast import (
    Assign, Seq, If, While, Block, Skip,
    Num, Var, BinOp, Compare, Or, Not,
)

class SiplRuntimeError(Exception):
    """Помилка під час виконання програми SIPL."""

    def __init__(self, message, span=None):
        self.message = message
        self.span = span
        if span is not None:
            text = f"Помилка виконання ({span}): {message}"
        else:
            text = f"Помилка виконання: {message}"
        super().__init__(text)


class Interpreter:
    """Виконує програму SIPL крок за кроком."""

    def __init__(self, max_steps=10000):
        self.max_steps = max_steps
        self.steps = 0

    def run(self, program, state):
        """Виконує програму на стані state і повертає кінцевий стан."""
        self.steps = 0
        state = dict(state)  
        self.exec_stmt(program.body, state)
        return state

    def count_step(self, node):
        """Рахує кроки і зупиняє програму, якщо їх забагато."""
        self.steps += 1
        if self.steps > self.max_steps:
            raise SiplRuntimeError(
                f"перевищено ліміт у {self.max_steps} кроків (нескінченний цикл)",
                node.span,
            )

    def exec_stmt(self, node, state):
        """Виконує оператор: змінює state"""
        self.count_step(node)

        if isinstance(node, Assign):
            state[node.name] = self.eval_expr(node.expr, state)

        elif isinstance(node, Seq):
            self.exec_stmt(node.first, state)
            self.exec_stmt(node.second, state)

        elif isinstance(node, If):
            if self.eval_cond(node.cond, state):
                self.exec_stmt(node.then_branch, state)
            else:
                self.exec_stmt(node.else_branch, state)

        elif isinstance(node, While):
            while self.eval_cond(node.cond, state):
                self.exec_stmt(node.body, state)

        elif isinstance(node, Block):
            self.exec_stmt(node.body, state)

        elif isinstance(node, Skip):
            pass

        else:
            raise SiplRuntimeError("невідомий оператор: " + type(node).__name__, node.span)

    def eval_expr(self, node, state):
        """Обчислює арифметичний вираз і повертає число."""
        if isinstance(node, Num):
            return node.value

        elif isinstance(node, Var):
            if node.name not in state:
                raise SiplRuntimeError(f"змінна '{node.name}' не має значення", node.span)
            return state[node.name]

        elif isinstance(node, BinOp):
            left = self.eval_expr(node.left, state)
            right = self.eval_expr(node.right, state)
            if node.op == "+":
                return left + right
            elif node.op == "-":
                return left - right
            elif node.op == "*":
                return left * right

        raise SiplRuntimeError("невідомий вираз: " + type(node).__name__, node.span)


    def eval_cond(self, node, state):
        """Обчислює умову і повертає True або False."""
        if isinstance(node, Compare):
            left = self.eval_expr(node.left, state)
            right = self.eval_expr(node.right, state)
            if node.op == "=":
                return left == right
            elif node.op == ">":
                return left > right

        elif isinstance(node, Or):
            return self.eval_cond(node.left, state) or self.eval_cond(node.right, state)

        elif isinstance(node, Not):
            return not self.eval_cond(node.cond, state)

        raise SiplRuntimeError("невідома умова: " + type(node).__name__, node.span)


def run_program(program, state, max_steps=10000):
    """Виконує програму і повертає кінцевий стан."""
    interpreter = Interpreter(max_steps)
    return interpreter.run(program, state)


def format_state(state):
    """Стан"""
    parts = []
    for name, value in state.items():
        parts.append(f"{name} ↦ {value}")
    return "[" + ", ".join(parts) + "]"