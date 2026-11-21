import ast
import math
import operator


class SafeExpression:
    FUNCTIONS = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        "exp": math.exp,
        "log": math.log,
        "log10": math.log10,
        "sqrt": math.sqrt,
        "abs": abs,
        "floor": math.floor,
        "ceil": math.ceil,
    }

    CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
    }

    BINARY_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
    }

    UNARY_OPERATORS = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def __init__(self, expression: str):
        expression = expression.replace("^", "**").strip()

        if not expression or len(expression) > 200:
            raise ValueError("Функция пустая или слишком длинная.")

        try:
            self.tree = ast.parse(expression, mode="eval")
        except SyntaxError as error:
            raise ValueError("Ошибка в записи функции.") from error

        if sum(1 for _ in ast.walk(self.tree)) > 100:
            raise ValueError("Слишком сложное выражение.")

        self.expression = expression
        self._validate(self.tree.body)

    def _validate(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(
                node.value, (int, float)
            ):
                raise ValueError("Разрешены только числовые константы.")

            if not math.isfinite(node.value):
                raise ValueError("Константа должна быть конечным числом.")

        elif isinstance(node, ast.Name):
            if node.id != "x" and node.id not in self.CONSTANTS:
                raise ValueError(f"Неизвестное имя: {node.id}")

        elif isinstance(node, ast.BinOp):
            if type(node.op) not in self.BINARY_OPERATORS:
                raise ValueError("Недопустимая операция.")

            self._validate(node.left)
            self._validate(node.right)

        elif isinstance(node, ast.UnaryOp):
            if type(node.op) not in self.UNARY_OPERATORS:
                raise ValueError("Недопустимая операция.")

            self._validate(node.operand)

        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Недопустимый вызов функции.")

            if node.func.id not in self.FUNCTIONS or node.keywords:
                raise ValueError("Неизвестная функция или аргументы.")

            if not node.args:
                raise ValueError("Функция должна иметь аргументы.")

            for argument in node.args:
                self._validate(argument)

        else:
            raise ValueError("Недопустимое математическое выражение.")

    def _evaluate(self, node, x: float) -> float:
        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.Name):
            if node.id == "x":
                return x

            return self.CONSTANTS[node.id]

        if isinstance(node, ast.BinOp):
            left = self._evaluate(node.left, x)
            right = self._evaluate(node.right, x)

            if isinstance(node.op, ast.Pow):
                if abs(right) > 1000 or abs(left) > 1e100:
                    raise ValueError("Слишком большая степень.")

            return self.BINARY_OPERATORS[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp):
            value = self._evaluate(node.operand, x)
            return self.UNARY_OPERATORS[type(node.op)](value)

        if isinstance(node, ast.Call):
            function = self.FUNCTIONS[node.func.id]
            arguments = [
                self._evaluate(argument, x)
                for argument in node.args
            ]

            return function(*arguments)

        raise ValueError("Не удалось вычислить выражение.")

    def __call__(self, x: float) -> float:
        try:
            result = self._evaluate(self.tree.body, x)
            result = float(result)
        except (ArithmeticError, TypeError, ValueError, OverflowError) as error:
            raise ValueError(f"Ошибка вычисления при x = {x:g}: {error}") from error

        if not math.isfinite(result):
            raise ValueError(f"Функция не определена при x = {x:g}.")

        return result
