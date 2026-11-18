from sipl.ast import (
    Assign, Seq, If, While, Block, Skip,
    Num, Var, BinOp, Compare, Or, Not,
)
from sipl.interpreter import Interpreter, format_state
from sipl.semantics import sem_P, sem_S, sem_B, ARITHMETIC, COMPARISON


def bool_text(value):
    """True/False -> true/false """
    if value:
        return "true"
    return "false"


def show_expr(node, state):
    """Вираз з підставленими значеннями"""
    if isinstance(node, Num):
        return str(node.value)
    elif isinstance(node, Var):
        return str(state[node.name])
    elif isinstance(node, BinOp):
        name = ARITHMETIC[node.op]
        return f"{name}({show_expr(node.left, state)}, {show_expr(node.right, state)})"


def show_cond(node, state):
    """Умова з підставленими значеннями"""
    if isinstance(node, Compare):
        name = COMPARISON[node.op]
        return f"{name}({show_expr(node.left, state)}, {show_expr(node.right, state)})"
    elif isinstance(node, Or):
        return f"or({show_cond(node.left, state)}, {show_cond(node.right, state)})"
    elif isinstance(node, Not):
        return f"neg({show_cond(node.cond, state)})"


class TermEvaluator:
    """Застосовує терм програми до стану і записує всі кроки"""

    def __init__(self, max_steps=10000)
        self.interpreter = Interpreter(max_steps)
        self.lines = []

    def log(self, text, level):
        """Додає рядок пояснення"""
        self.lines.append("  " * level + text)

    def run(self, program, state):
        """Повертає кінцевий стан """
        self.lines = []
        self.interpreter.steps = 0
        state = dict(state)

        self.log("Терм: " + sem_P(program), 0)
        self.log("Початковий стан: st = " + format_state(state), 0)
        self.eval_stmt(program.body, state, 0)
        self.log("Результат: " + format_state(state), 0)
        return state, self.lines

    def eval_stmt(self, node, state, level):
        """Застосовує терм оператора до стану і записує, що відбулося."""
        self.interpreter.count_step(node)

        if isinstance(node, Assign):
            # AF_AS: AS^x(fa)(st) = st∇[x ↦ fa(st)]
            value = self.interpreter.eval_expr(node.expr, state)
            calculation = show_expr(node.expr, state)
            state[node.name] = value
            if calculation == str(value):
                step = f"{node.name} ↦ {value}"
            else:
                step = f"{node.name} ↦ {calculation} = {value}"
            self.log(f"{sem_S(node)}: {step}  =>  {format_state(state)}   (AF_AS)", level)

        elif isinstance(node, Seq):
            # AF_SEQ: (f • g)(st) = g(f(st)) 
            self.eval_stmt(node.first, state, level)
            self.eval_stmt(node.second, state, level)

        elif isinstance(node, If):
            # AF_IF
            result = self.interpreter.eval_cond(node.cond, state)
            if result:
                branch = "then"
            else:
                branch = "else"
            self.log(f"Умова {sem_B(node.cond)} = {show_cond(node.cond, state)} = "
                     f"{bool_text(result)}, виконуємо гілку {branch}   (AF_IF)", level)
            if result:
                self.eval_stmt(node.then_branch, state, level + 1)
            else:
                self.eval_stmt(node.else_branch, state, level + 1)

        elif isinstance(node, While):
            # AF_WH
            iteration = 0
            self.log(f"st0 = {format_state(state)}", level)
            while True:
                result = self.interpreter.eval_cond(node.cond, state)
                self.log(f"Умова циклу {sem_B(node.cond)} = {show_cond(node.cond, state)} = "
                         f"{bool_text(result)}   (AF_WH)", level)
                if not result:
                    self.log("Умова хибна - вихід з циклу", level)
                    break
                iteration += 1
                self.log(f"Ітерація {iteration}:", level)
                self.eval_stmt(node.body, state, level + 1)
                self.log(f"st{iteration} = {format_state(state)}", level)

        elif isinstance(node, Block):
            # begin S end -  S
            self.eval_stmt(node.body, state, level)

        elif isinstance(node, Skip):
            # AF_ID: id(st) = st
            self.log(f"id: стан не змінюється  =>  {format_state(state)}   (AF_ID)", level)


def explain(program, state, max_steps=10000):
    """Зручна функція: повертає (кінцевий стан, список рядків пояснення)."""
    evaluator = TermEvaluator(max_steps)
    return evaluator.run(program, state)