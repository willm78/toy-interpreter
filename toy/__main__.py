import sys
from .imp_lexer import imp_lex
from .parser import aexp


if __name__ == '__main__':
    """
    $ echo '1 + 2 * 3' >foo.imp
    $ python imp_parser_driver.py foo.imp aexp
    Result(BinopAexp(+, IntAexp(1), BinopAexp(*, IntAexp(2), IntAexp(3))), 5)
    """
    if len(sys.argv) != 3:
        sys.stderr.write('usage: %s filename parsername' % sys.argv[0])
        sys.exit(1)
    filename = sys.argv[1]
    with open(filename) as f:
        characters = f.read()
    tokens = imp_lex(characters)
    parser = globals()[sys.argv[2]]()
    result = parser(tokens, 0)
    print(result)