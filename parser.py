import re
import math
from lark import Lark, InlineTransformer, Token

grammar = Lark(
    r"""
    ?start  : assign* comp?
    ?assign: NAME "=" comp
    ?comp  : expr ">" expr  -> gt
        | expr ">=" expr -> ge
        | expr "<" expr  -> lt
        | expr "<=" expr -> le
        | expr "!=" expr -> ne
        | expr "==" expr -> eq
        | expr
    ?expr  : expr "+" term  -> add
        | expr "-" term  -> sub
        | term
    ?term  : term "*" pow   -> mul
        | term "/" pow   -> div
        | pow
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

class CalcTransformer(InlineTransformer):
    from operator import add, sub, mul, truediv as div, pow as exp, gt, ge, lt, le, ne, eq

    def __init__(self):
        super().__init__()
        self.variables = {k: v for k, v in vars(math).items() if not k.startswith("_")}
        self.variables.update(max=max, min=min, abs=abs)
        self.tmp = {}

    def number(self, token):
        try:
            return int(token)
        except:
            return float(token)

    def const(self, token):
        value = self.variables[token]
        return value

    def var(self, token):
        if token in self.variables:
            return self.variables[token]
        elif token.startswith("-") and token[1:] in self.variables:
            return -self.variables[token[1:]]
        else:
            return self.tmp[token]
    
    def function_transform(self, name, *args):
        name = str(name)
        fn = self.variables[name.split('-')[-1]]
        if name.startswith('-'):
            return -fn(*args)
        return fn(*args)
    
    def assign(self, name, value):
        self.tmp[name] = value
        return self.tmp[name]
    
    def start(self, *args):
        return args[-1]