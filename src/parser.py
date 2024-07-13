import ply.lex as lex
import ply.yacc as yacc

NUMBER, PHASE, ROUND, PIPELINE, RESOURCE, GROUP = 1, 2, 3, 4, 5, 6

class Entity:
    def __init__(self, value, type):
        self.value = value
        self.type = type

class BinaryComparison:
    def __init__(self, lpart: Entity, rpart: Entity, operator: str):
        self.lpart = lpart
        self.rpart = rpart
        self.operator = operator

class RuleParser:
    def __init__(self):
        self._parser = yacc.yacc(optimize=True)
        self.lexer = lex.lex(optimize=True)

    def parse(self, data):
        return self._parser.parse(data, lexer=self.lexer)

# Full set of tokens
tokens = (
        'NUMBER',
        'PHASE_ID',
        'ROUND_ID',
        'PIPELINE_ID',
        'RESOURCE_ID',
        'GROUP_ID',
        'EQUAL',
        'NEQUAL',
        'GTHAN',
        'LTHAN', 
        'LETHAN',
        'GETHAN')

 # regular expressions for arithmetic tokens
t_EQUAL = r'\='
t_NEQUAL = r'\!\='
t_GTHAN = r'\>\='
t_LTHAN = r'\<\='
t_LETHAN = r'\<'
t_GETHAN = r'\>'

# ignored characters    
t_ignore = ' \t'

def t_NEWLINE(t):
        r'\n+'
        t.lexer.lineno += t.value.count('\n')

def t_PHASE_ID(t):
    r'PHASE_\d+'
    t.value = Entity(int(t.value[6:]), PHASE)
    return t

def t_ROUND_ID(t):
    r'ROUND_\d+'
    t.value = Entity(int(t.value[6:]), ROUND)
    return t

def t_PIPELINE_ID(t):
    r'PIPELINE_\d+'
    t.value = Entity(int(t.value[9:]), PIPELINE)
    return t

def t_GROUP_ID(t):
    r'GROUP_\d+'
    t.value = Entity(int(t.value[6:]), GROUP)
    return t

def t_RESOURCE_ID(t):
    r'RESOURCE_\d+'
    t.value = Entity(int(t.value[9:]), RESOURCE)
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = Entity(int(t.value), NUMBER)
    return t

def t_error(t):
        print("Illegal character '%s'" % t.value[0])

def p_expression(p):
    '''expression : expression rule
                  | rule'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = p[1] + [p[2]]

def p_rule(p):
    '''rule : leftarg GTHAN factor
            | leftarg LTHAN factor
            | leftarg GETHAN factor
            | leftarg LETHAN factor
            | leftarg NEQUAL factor
            | leftarg EQUAL factor'''
    p[0] = BinaryComparison(p[1], p[3], p[2])

def p_leftarg(p):
    '''leftarg : RESOURCE_ID
            | GROUP_ID'''
    p[0] = p[1]

def p_factor(p):
    '''factor : NUMBER
            | PHASE_ID
            | ROUND_ID
            | GROUP_ID
            | PIPELINE_ID
            | RESOURCE_ID'''
    p[0] = p[1]

def p_error(p):
    print("Syntax error: ", p)
    
if __name__ == "__main__":     
    dsl_code = """
    RESOURCE_2 > 30
    RESOURCE_2 < GROUP_30
    RESOURCE_2 > PHASE_4
    RESOURCE_2 >= ROUND_2
    RESOURCE_2 > PIPELINE_14
    RESOURCE_2 > RESOURCE_35
    GROUP_2 = 30
    GROUP_2 > GROUP_30
    GROUP_2 > PHASE_4
    GROUP_2 <= ROUND_2
    GROUP_2 > PIPELINE_14
    GROUP_2 != RESOURCE_35
    """
    parser = RuleParser()
    print(parser.parse(dsl_code))
