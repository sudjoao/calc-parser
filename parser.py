import re
import math
from lark import Lark, InlineTransformer, Token


# Implemente a gramática aqui! Você pode testar manualmente seu código executando
# o arquivo calc.py e testá-lo utilizando o pytest.
grammar = Lark(
    r"""
    ?start  : assign* comp?
    ?assign: NAME "=" comp
    ?comp  : expr "<" expr  -> lt
        | expr "<=" expr -> le
        | expr ">" expr  -> gt
        | expr ">=" expr -> ge
        | expr "!=" expr -> ne
        | expr "==" expr -> eq
        | expr
    ?term  : term "*" pow   -> mul
        | term "/" pow   -> div
        | pow
    ?expr  : expr "-" term  -> sub
        | expr "+" term  -> add
        | term
    ?pow   : atom "^" pow   -> exp
        | atom
    ?atom  : NUMBER                        -> number
        | NAME "(" expr ")"             -> function_transform
        | NAME "(" expr ("," expr)* ")" -> function_transform
        | NAME                          -> var
        | "(" expr ")"
    NAME   : /[-+]?\w+/
    NUMBER : /-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/
    %ignore /\s+/
    %ignore /\#.*/
    """
)

exprs = [
    "pi",
    "sin"
]


for src in exprs:
    tree = grammar.parse(src)
    print(src)
    print(tree.pretty())
    print('-' * 40)

class CalcTransformer(InlineTransformer):
    from operator import add, sub, mul, truediv as div  # ... e mais! 

    def __init__(self):
        super().__init__()
        self.variables = {k: v for k, v in vars(math).items() if not k.startswith("_")}
        self.variables.update(max=max, min=min, abs=abs)
        self.vars = {}

    def number(self, token):
        try:
            return int(token)
        except:
            return float(token)

    def assign(self, name, value):
        self.env[name] = value
        return self.env[name]


    def var(self, token):
        if token in self.variables:
            return self.variables[token]
        elif token[0].startswith('-') and token[1:] in self.variables:
            return -self.variables[token[1:]]
        else:
            return self.env[token]

    def function_transform(self, name, *args):
        name = str(name)
        fn = self.variables[name.split('-')[-1]]
        if name.startswith('-'):
            return -fn(*args)
        return fn(*args)

    def start(self, *args):
        return args[-1]
