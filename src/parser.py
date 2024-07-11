import ply.lex as lex
import ply.yacc as yacc

# Token definitions
tokens = (
        'NUMBER',
        'PHASE_ID',
        'ROUND_ID',
        'PIPELINE_ID',
        'RESOURCE_ID',
        'EQUAL',
        'NEQUAL',
        'GTHAN',
        'LTHAN', 
        'LETHAN',
        'GETHAN')

# Ignored characters
t_ignore = ' \t'

# Token regular expressions
t_EQUAL = r'\='
t_NEQUAL = r'\!\='
t_GTHAN = r'\>\='
t_LTHAN = r'\<\='
t_LETHAN = r'\<'
t_GETHAN = r'\>'

# Variables
variables = {}
pipeline_count = 0
phase_count = 0
resource_count = 0
round_count = 0
rule_count = 0

# Token definition for newline, print, vector and 
# matrix identifiers, generic identifiers, and numbers
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')

def t_PHASE_ID(t):
    r'PHASE_\d+'
    t.value = ("PHASE", int(t.value[6:]))
    return t

def t_ROUND_ID(t):
    r'ROUND_\d+'
    t.value = ("ROUND", int(t.value[6:]))
    return t

def t_PIPELINE_ID(t):
    r'PIPELINE_\d+'
    t.value = ("PIPELINE", int(t.value[9:]))
    return t

def t_RESOURCE_ID(t):
    r'RESOURCE_\d+'
    t.value = ("RESOURCE", int(t.value[9:]))
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_error(t):
        print("Illegal character '%s'" % t.value[0])

# ---- PROGRAM ----
def p_program(p):
    '''program : NUMBER NUMBER NUMBER NUMBER NUMBER expression
               | NUMBER NUMBER NUMBER NUMBER'''
    if len(p) == 7:
        p[0] = (p[1], p[2], p[3], p[4], p[5], p[6])
    elif len(p) == 5:
        p[0] = (p[1], p[2], p[3], p[4], 0, [])

# def p_rgroup(p):
#     '''rgroup : NUMBER rgroup
#               | expression'''
#     if len(p) == 2:
#         p[0] = p[1]
#     elif len(p) == 3:
#         p[0] = [p[1]] + p[2]

def p_expression(p):
    '''expression : expression rule
                  | rule'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = p[1] + [p[2]]

def p_rule(p):
    '''rule : RESOURCE_ID GTHAN factor
            | RESOURCE_ID LTHAN factor
            | RESOURCE_ID GETHAN factor
            | RESOURCE_ID LETHAN factor
            | RESOURCE_ID NEQUAL factor
            | RESOURCE_ID EQUAL factor'''
    p[0] = (p[1], p[2], p[3])

def p_factor(p):
    '''factor : NUMBER
              | PHASE_ID
              | ROUND_ID
              | PIPELINE_ID
              | RESOURCE_ID'''
    p[0] = p[1]

def p_error(p):
    print("Syntax error: ", p)

# Build the lexer and parser
lexer = lex.lex(debug=True)
parser = yacc.yacc(debug=True)

# Parsing and executing DSL code
dsl_code = """
3 4 5 5 5
RESOURCE_4 > PHASE_30
RESOURCE_5 > 30
RESOURCE_2 > 30
"""

print(parser.parse(dsl_code))
