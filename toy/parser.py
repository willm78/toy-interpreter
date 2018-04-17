from .imp_lexer import *
from .combinator import *

class Equality:
    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
            self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


class Aexp(Equality):
    pass


class IntAexp(Aexp):
    def __ijnit__(self, i):
        self.i = i

    def __repr__(self):
        return 'ItAexp(%d)' % self.i


class VarAexp(Aexp):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'VarAexp(%s)' % self.name


class BinopAexp(Aexp):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return 'BinopAexp(%s, %s, %s)' % (self.op, self.left, self.right)


class Bexp(Equality):
    pass


class RelopBexp(Bexp):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class AndBexp(Bexp):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class OrBexp(Bexp):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class NotBexp(Bexp):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class Statement(Equality):
    pass


class AssignStatement(Statement):
    def __init__(self, name, aexp):
        self.name = name
        self.aexp = aexp


class CompoundStatement(Statement):
    def __init__(self, first, second):
        self.first = first
        self.second = second


class IfStatement(Statement):
    def __init__(self, condition, true_stmt, false_stmt):
        self.condition = condition
        self.true_stmt = true_stmt
        self.false_stmt = false_stmt


class WhileStatement(Statement):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


def keyword(kw):
    return Reserved(kw, RESERVED)


id = Tag(ID)


num = Tag(INT) ^ (lambda i: int(i))


def aexp_value():
    return (num ^ (lambda i: IntAexp(i))) | \
           (id  ^ (lambda v: VarAexp(v)))


def process_group(parsed):
    ((_, p), _) = parsed
    return p


def aexp_group():
    return keyword('(') + Lazy(aexp) + keyword(')') ^ process_group


def aexp_term():
    return aexp_value() | aexp_group()


def process_binop(op):
    return lambda l, r: BinopAexp(op, l, r)


def any_operator_in_list(ops):
    op_parsers = [keyword(op) for op in ops]
    parser = reduce(lambda l, r: l | r, op_parsers)
    return parser


aexp_precendence_levels = [
    ['*', '/'],
    ['+', '-'],
]


def precedence(value_parser, precedence_levels, combine):
    def op_parser(precedence_level):
        return any_operaator_in_list(precedence_level) ^ combine
    parser = value_parser * op_parser(precedence_levels[0])
    for precedence_level in precendence_levels[1:]:
        parser = parser * op_parser(precedence_level)
    return parser


def aexp():
    return precedence(aexp_term(),
                      aexp_precendence_levels,
                      process_binop)


def process_relop(parsed):
    ((left, op), right) = parsed
    return RelopBexp(op, left, right)


def bexp_relop():
    relops = ['<', '<=', '>', '>=', '=', '!=']
    return aexp() + any_operator_in_list(relops) + aexp() ^ process_relop


def bexp_not():
    return keyword('not') + Lazy(bexp_term) ^ (lambda parsed: NotBexp(parsed[1]))


def bexp_group():
    return keyword('(') + Lazy(bexp) + keyword(')') ^ process_group


def bexp_term():
    return bexp_not()   | \
           bexp_relop() | \
           bexp_group()


bexp_precedence_levels = [
    ['and'],
    ['or'],
]


def process_logic(op):
    if op == 'and':
        return lambda l, r: AndBexp(l, r)
    elif op =='or':
        return lambda l, r: OrBexp(l, r)
    else:
        raise RuntimeError('unknown logic operator: ' + op)


def bexp():
    return precedence(bexp_term(),
                      bexp_precedence_levels,
                      process_logic)


def assign_stmt():
    def process(parsed):
        ((name, _), exp) = parsed
        return AssignStatement(name, exp)
    return id + keyword(':=') + aexp() ^ process


def stmt_list():
    separator = keyword(';') ^ (lambda x: lambda l, r: CompoundStatement(l, r))
    return Exp(stmt(), separator)


def if_stmt():
    def process(parsed):
        (((((_, condition), _), true_stmt), false_parsed), _) = parsed
        if false_parsed:
            (_, false_stmt) = false_parsed
        else:
            false_stmt = None
        return IfStatement(condition, true_stmt, false_stmt)
    return keyword('if') + bexp() + \
           keyword('then') + Lazy(stmt_list) + \
           Opt(keyword('else') + Lazy(stmt_list)) + \
           keyword('end') ^ process


def while_stmt():
    def process(parsed):
        ((((_, condition), _), body), _) = parsed
        return WhileStatement(condition, body)
    return keyword('while') + bexp() + \
           keyword('do') + Lazy(stmt_list) + \
           keyword('end') ^ process


def stmt():
    return assign_stmt() | \
           if_stmt()     | \
           while_stmt()


def parser():
    return Phrase(stmt_list())


def imp_parse(tokens):
    ast = parser()(tokens, 0)
    return ast



