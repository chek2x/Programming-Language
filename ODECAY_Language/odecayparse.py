import sys
from odecaylex import *
from odecayinterpret import *

# Parser object keeps track of current token and checks if the code matches the grammar.
class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter

        self.symbols = list()            # Variables declared so far.

        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken()    # Call this twice to initialize current and peek.

    # Return true if the current token matches.
    def checkToken(self, kind):
        return kind == self.curToken.kind

    # Return true if the next token matches.
    def checkPeek(self, kind):
        return kind == self.peekToken.kind

    # Try to match current token. If not, error. Advances the current token.
    def find(self, kind):
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + ", got " + self.curToken.kind.name)
        self.nextToken()

    # Advances the current token.
    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()
        # No need to worry about passing the EOF, lexer handles that.

    def abort(self, message):
        sys.exit("Error. " + message)
    

    # VVVVV PRODUCTION RULES VVVVV #

    # program ::= {statement}
    def program(self):
        print("PROGRAM START")
        self.emitter.headerLine("def main():")

        # Since some newlines are required in our grammar, need to skip the excess.
        while self.checkToken(TokenType.EWLINENAY):
            self.nextToken()

        # Parse all the statements in the program.
        while not self.checkToken(TokenType.EOF):
            self.statement()

        # Wrap things up.
        self.emitter.emitLine("\nmain()")
        
    
    # One of the following statements...
    def statement(self):
        # Check the first token to see what kind of statement this is.

        # "INTPRAY" (expression | string)
        if self.checkToken(TokenType.INTPRAY):
            print("EXEC STATEMENT_PRINT")
            self.nextToken()

            if self.checkToken(TokenType.INGSTRAY):
                # Simple string, so print it.
                self.emitter.emitLine("\tprint(\'" + self.curToken.text + "\')")
                self.nextToken()
            else:
                self.emitter.emit("\tprint(")
                self.expression()
                self.emitter.emitLine(")")

        # "IFYAY" comparison "ENTHAY" nl {statement} "ENDIFYAY" nl
        elif self.checkToken(TokenType.IFYAY):
            print("EXEC STATEMENT_IF")
            self.nextToken()
            self.emitter.emit("\tif ")
            self.comparison()

            self.find(TokenType.ENTHAY)
            self.nl()
            self.emitter.emitLine(":")

            # Zero or more statements in the body.
            while not self.checkToken(TokenType.ENDIFYAY):
                self.emitter.emit("\t")
                self.statement()

            self.find(TokenType.ENDIFYAY)

            # ["ELSEYAY" "ENTHAY" nl {statement} "ENDIFYAY" nl]
            if self.checkPeek(TokenType.ELSEYAY):
                print("EXEC STATEMENT_IF_ELSE")
                self.nextToken()
                self.nextToken()
                self.emitter.emit("\telse")

                self.find(TokenType.ENTHAY)
                self.nl()
                self.emitter.emitLine(":")

                # Zero or more statements in the body.
                while not self.checkToken(TokenType.ENDIFYAY):
                    self.emitter.emit("\t")
                    self.statement()

                self.find(TokenType.ENDIFYAY)

        # "ETLAY" variable "=" (expression | primary | boolean)
        elif self.checkToken(TokenType.ETLAY):
            print("EXEC STATEMENT_ASSIGN_VAR")
            self.nextToken()

            #  Check if ident exists in symbol table. If not, declare it.
            if self.curToken.text not in self.symbols:
                self.symbols.append(self.curToken.text)

            self.emitter.emit("\t" + self.curToken.text + " = ")
            self.find(TokenType.IDENTYAY)
            self.find(TokenType.EQUALYAY)

            if self.checkToken(TokenType.INGSTRAY):
                self.emitter.emit("\'" + self.curToken.text + "\'")
                self.nextToken()
            elif self.checkToken(TokenType.UETRAY) or self.checkToken(TokenType.ALSEFAY):
                self.boolean()
            else:
                self.expression()
            self.emitter.emit("\n")

        # "INPUTYAY" ["INTYAY"] variable
        elif self.checkToken(TokenType.INPUTYAY):
            print("EXEC STATEMENT_INPUT")
            self.nextToken()

            #If variable doesn't already exist, declare it.
            if self.curToken.text not in self.symbols:
                self.symbols.append(self.curToken.text)

            #Accept input using input() in py
            if self.checkToken(TokenType.INTYAY):
                self.nextToken()
                if self.curToken.text not in self.symbols:
                    self.symbols.append(self.curToken.text)
                self.emitter.emitLine("\t" + self.curToken.text + " = int(input())")
            else:
                self.emitter.emitLine("\t" + self.curToken.text + " = input()")

            self.find(TokenType.IDENTYAY)

        # Invalid Statement Error
        else:
            self.abort("Invalid statement at " + self.curToken.text + " (" + self.curToken.kind.name + ")")

        # Newline.
        self.nl()

    # comparison ::= (string | expression | boolean) (("==" | "!=" | ">" | ">=" | "<" | "<=") ( string | expression | boolean))+
    def comparison(self):
        print("EXEC COMPARISON")

        # (expression | boolean)
        if self.checkToken(TokenType.UETRAY) or self.checkToken(TokenType.ALSEFAY):
            self.boolean()
        elif self.checkToken(TokenType.INGSTRAY):
            self.emitter.emit("\'" + self.curToken.text+ "\'")
            self.nextToken()
        else:
            self.expression()

        # Must be at least one comparison operator and another expression.
        if self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            if self.checkToken(TokenType.UETRAY) or self.checkToken(TokenType.ALSEFAY):
                self.boolean()
            elif self.checkToken(TokenType.INGSTRAY):
                self.emitter.emit("\'" + self.curToken.text+ "\'")
                self.nextToken()
            else:
                self.expression()
        # Can have 0 or more comparison operator and expressions.
        while self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            if self.checkToken(TokenType.UETRAY) or self.checkToken(TokenType.ALSEFAY):
                self.boolean()
            elif self.checkToken(TokenType.INGSTRAY):
                self.emitter.emit("\'" + self.curToken.text+ "\'")
                self.nextToken()
            else:
                self.expression()

    # Return true if the current token is a comparison operator.
    def isComparisonOperator(self):
        return self.checkToken(TokenType.EATERGRAY) or self.checkToken(TokenType.EQEATERGRAY) or self.checkToken(TokenType.ESSLAY) or self.checkToken(TokenType.EQESSLAY) or self.checkToken(TokenType.EQEQUALYAY) or self.checkToken(TokenType.OTEQUALNAY)

    # expression ::= term {( "+" | "-" ) term}
    def expression(self):
        print("EXEC EXPRESSION")

        self.term()
        # Can have 0 or more +/- and expressions.
        while self.checkToken(TokenType.USPLAY) or self.checkToken(TokenType.INUSMAY):
            self.emitter.emit(' ' + self.curToken.text + ' ')
            self.nextToken()
            self.term()

    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        print("EXEC TERM")

        self.unary()
        # Can have 0 or more *// and expressions.
        while self.checkToken(TokenType.ARSTAY) or self.checkToken(TokenType.ASHSLAY):
            self.emitter.emit(' ' + self.curToken.text + ' ')
            self.nextToken()
            self.unary()

    # unary ::= ["+" | "-"] primary
    def unary(self):
        print("EXEC UNARY")

        # Optional unary +/-
        if self.checkToken(TokenType.USPLAY) or self.checkToken(TokenType.INUSMAY):
            self.emitter.emit(self.curToken.text)
            self.nextToken()        
        self.primary()

    # primary ::= number | ident
    def primary(self):
        print("EXEC PRIMARY (" + self.curToken.text + ")")

        if self.checkToken(TokenType.UMBERNAY): 
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENTYAY):
            # Ensure the variable already exists.
            if self.curToken.text not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.curToken.text)
            
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            if self.checkToken(TokenType.UPYAY):
                self.emitter.emit(' + 1')
                self.nextToken()
            elif self.checkToken(TokenType.OWNDAY):
                self.emitter.emit(' - 1')
                self.nextToken()
        elif self.checkToken(TokenType.OPENYAY_PAR):
            self.emitter.emit("( ")
            self.nextToken()
            self.expression()
            self.find(TokenType.OSECLAY_PAR)
            self.emitter.emit(" )")
        else:
            # Error!
            self.abort("Unexpected token at " + self.curToken.text)

    # boolean ::= "UETRAY" | "ALSEFAY"
    def boolean(self):
        print("EXEC BOOLEAN")

        if self.checkToken(TokenType.UETRAY):
            self.emitter.emit('True')
            self.nextToken()
        elif self.checkToken(TokenType.ALSEFAY):
            self.emitter.emit('False')
            self.nextToken()
        else:
            # Error!
            self.abort("Unexpected token at " + self.curToken.text)

    # nl ::= '\n'+
    def nl(self):
        print("EXEC EWLINENAY")
		
        # Require at least one newline.
        self.find(TokenType.EWLINENAY)
        # But we will allow extra newlines too, of course.
        while self.checkToken(TokenType.EWLINENAY):
            self.nextToken()