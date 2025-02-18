from interp import Add, Sub, Mul, Not, Div, Neg, Or, Let, Name, Lit, Ifnz, Letfun, Expr, App, run, Combine, And, Eq, lighten, Darken,Lt
from lark import Lark, Token, ParseTree, Transformer
from lark.exceptions import VisitError
from pathlib import Path

parser = Lark(Path('expr.lark').read_text(),start='expr',ambiguity='explicit', lexer = "basic")
# to check against ambiguity:
#parser = Lark(Path('expr.lark').read_text(),start='expr',parser='lalr',strict=True, lexer = "basic")

class ParseError(Exception): 
    pass

def parse(s:str) -> ParseTree:
    try:
        return parser.parse(s)
    except Exception as e:
        raise ParseError(e)

class AmbiguousParse(Exception):
    pass

class ToExpr(Transformer[Token,Expr]):
    '''Defines a transformation from a parse tree into an AST'''
    def plus(self, args:tuple[Expr,Expr]) -> Expr:
        return Add(args[0],args[1])
    def times(self, args:tuple[Expr,Expr]) -> Expr:
        return Mul(args[0],args[1])
    def minus(self, args:tuple[Expr,Expr]) -> Expr:
        return Sub(args[0],args[1])
    def divide(self, args:tuple[Expr,Expr]) -> Expr:
        return Div(args[0],args[1])
    def neg(self, args:tuple[Expr]) -> Expr:
        return Neg(args[0])
    def let(self, args:tuple[Token,Expr,Expr]) -> Expr:
        return Let(args[0].value,args[1],args[2]) 
    def id(self, args:tuple[Token]) -> Expr:
        return Name(args[0].value)
    def int(self,args:tuple[Token]) -> Expr:
        return Lit(int(args[0].value))
    def true(self, args:tuple) -> Expr:
        return Lit(True)
    def false(self, args:tuple) -> Expr:
        return Lit(False)
    def ifnz(self,args:tuple[Expr,Expr,Expr]) -> Expr:
        return Ifnz(args[0],args[1],args[2])
    def args(self,myargs:list[Expr]) -> list[Expr]:
        return myargs   
    def params(self,args:list[Token]) -> list[str]:
        return [t.value for t in args]
    def letfun(self,args:tuple[Token,list[str],Expr,Expr]) -> Expr:
        return Letfun(args[0].value,args[1],args[2],args[3])
    def app(self,args:tuple[Expr,list[Expr]]) -> Expr:
        return App(args[0],args[1])    
    def combine(self, args:tuple[Expr,Expr]) -> Expr:
        return Combine(args[0], args[1])
    def lighten(self, args:tuple[Expr]) -> Expr:
        return lighten(args[0])
    def Darken(self, args:tuple[Expr]) -> Expr:
        return Darken(args[0])
    def andexpr(self, args:tuple[Expr,Expr]) -> Expr:
        return And(args[0], args[1])
    def orexpr(self, args:tuple[Expr,Expr]) -> Expr:
        return Or(args[0], args[1])
    def eqexpr(self, args:tuple[Expr,Expr]) -> Expr:
        return Eq(args[0], args[1])
    def lessexpr(self, args:tuple[Expr,Expr]) -> Expr:
        return Lt(args[0], args[1])
    def notexpr(self, args:tuple[Expr]) -> Expr:
        return Not(args[0])

    def _ambig(self,_) -> Expr:    # ambiguity marker
        raise AmbiguousParse()

def genAST(t:ParseTree) -> Expr:
    '''Applies the transformer to convert a parse tree into an AST'''
    # boilerplate to catch potential ambiguity error raised by transformer
    try:
        return ToExpr().transform(t)               
    except VisitError as e:
        if isinstance(e.orig_exc,AmbiguousParse):
            raise AmbiguousParse()
        else:
            raise e

def driver():
    while True:
        try:
            s = input('expr: ')
            t = parse(s)
            print("raw:", t)    
            print("pretty:")
            print(t.pretty())
            ast = genAST(t)
            print("raw AST:", repr(ast))  # use repr() to avoid str() pretty-printing
            run(ast)                      # pretty-prints and executes the AST
        except AmbiguousParse:
            print("ambiguous parse")                
        except ParseError as e:
            print("parse error:")
            print(e)
        except EOFError:
            break

driver()


''' In this project milestone we have added 2 new
files. Those files are expr.lark and parse_run. What 
This program does is that it is a custom expression language. 
this program reads the expression form the user, then it 
parses it into a parse tree, transforms the parse tree to 
an AST and then executes tht AST. 


The expr.lark file defines the grammer for the custom expression. 
This gammer specifies the syntax rules for valid expressions in 
the language. epr.lark also combines and defines how expressions
are structered and how they can be combined.
'''