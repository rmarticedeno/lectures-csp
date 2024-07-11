import ply.lex as lex
import ply.yacc as yacc

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

def t_GROUP_ID(t):
    r'GROUP_\d+'
    t.value = ("GROUP", int(t.value[6:]))
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

def p_rule(p):
    '''rule : leftarg GTHAN factor
            | leftarg LTHAN factor
            | leftarg GETHAN factor
            | leftarg LETHAN factor
            | leftarg NEQUAL factor
            | leftarg EQUAL factor'''
    p[0] = (p[1], p[2], p[3])

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

class RuleParser:
    def __init__(self):
        self._parser = yacc.yacc(optimize=True)
        self.lexer = lex.lex(optimize=True)

    def parse(self, data):
        return self._parser.parse(data, lexer=self.lexer)
    
if __name__ == "__main__":     
    dsl_code = """
    RESOURCE_2 > GROUP_30
    """
    parser = RuleParser()
    print(parser.parse(dsl_code))
