import enum
import sys

class Token:
    def __init__(self, tokenText, tokenKind):
        self.text = tokenText   # The token's actual text. Used for identifiers, strings, and numbers.
        self.kind = tokenKind   # The TokenType that this token is classified as.

    def checkIfKeyword(tokenText):
        for kind in TokenType:
            # Relies on all keyword enum values being 1XX.
            if kind.name == tokenText and kind.value >= 100 and kind.value < 200:
                return kind
        return None

class Lexer:
    def __init__(self, input):
        self.source = input + '\n' # Source code to lex as a string. Append a newline to simplify lexing/parsing the last token/statement.
        self.curChar = ''   # Current character in the string.
        self.curPos = -1    # Current position in the string.
        self.nextChar()

    # Process the next character.
    def nextChar(self):
        self.curPos += 1
        if self.curPos >= len(self.source):
            self.curChar = '\0'  # EOF
        else:
            self.curChar = self.source[self.curPos]
    # Return the lookahead character.
    def peek(self):
        if self.curPos + 1 >= len(self.source):
            return '\0'
        return self.source[self.curPos+1]

    # Invalid token found, print error message and exit.
    def abort(self, message):
        sys.exit("Lexing error. " + message)
		
    # Skip whitespace except newlines, which we will use to indicate the end of a statement.
    def skipWhitespace(self):
        while self.curChar == ' ' or self.curChar == '\t' or self.curChar == '\r':
            self.nextChar()
		
    # Skip comments in the code.
    def skipComment(self):
        if self.curChar == '/':
            if self.peek() == '/':
                while self.curChar != '\n':
                    self.nextChar()

    # Return the next token.
    def getToken(self):
        self.skipWhitespace()
        self.skipComment()
        token = None

        # Check the first character of this token to see if we can decide what it is.
        # If it is a multiple character operator (e.g., !=), number, identifier, or keyword then we will process the rest.

        #Operators
        if self.curChar == '+':
            # Check whether this token is + or ++
            if self.peek() == '+':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.UPYAY)
            else:
                token = Token(self.curChar, TokenType.USPLAY)
        elif self.curChar == '-':
            # Check whether this token is - or --
            if self.peek() == '-':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.OWNDAY)
            else:
                token = Token(self.curChar, TokenType.INUSMAY)
        elif self.curChar == '*':
            token = Token(self.curChar, TokenType.ARSTAY)
        elif self.curChar == '/':
            token = Token(self.curChar, TokenType.ASHSLAY)

        #Comparators
        elif self.curChar == '=':
            # Check whether this token is = or ==
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.EQEQUALYAY)
            else:
                token = Token(self.curChar, TokenType.EQUALYAY)
        elif self.curChar == '>':
            # Check whether this is token is > or >=
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.EQEATERGRAY)
            else:
                token = Token(self.curChar, TokenType.EATERGRAY)
        elif self.curChar == '<':
                # Check whether this is token is < or <=
                if self.peek() == '=':
                    lastChar = self.curChar
                    self.nextChar()
                    token = Token(lastChar + self.curChar, TokenType.EQESSLAY)
                else:
                    token = Token(self.curChar, TokenType.ESSLAY)
        elif self.curChar == '!':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.OTEQUALNAY)
            else:
                self.abort("Expected !=, got !" + self.peek())

        #Parentheses
        elif self.curChar == '(':
            token = Token(self.curChar, TokenType.OPENYAY_PAR)
        elif self.curChar == ')':
            token = Token(self.curChar, TokenType.OSECLAY_PAR)

        #String
        elif self.curChar == '\'':
            # Get characters between quotations.
            self.nextChar()
            startPos = self.curPos

            while self.curChar != '\'':
                # Don't allow special characters in the string. No escape characters, newlines, tabs, or %.
                # We will be using C's printf on this string.
                if self.curChar == '\r' or self.curChar == '\n' or self.curChar == '\t' or self.curChar == '\\' or self.curChar == '%':
                    self.abort("Illegal character in string: " + self.curChar)
                self.nextChar()

            tokText = self.source[startPos : self.curPos] # Get the substring.
            token = Token(tokText, TokenType.INGSTRAY)

        #Number
        elif self.curChar.isdigit():
            # Leading character is a digit, so this must be a number.
            # Get all consecutive digits and decimal if there is one.
            startPos = self.curPos
            while self.peek().isdigit():
                self.nextChar()
            if self.peek() == '.': # Decimal!
                self.nextChar()

                # Must have at least one digit after decimal.
                if not self.peek().isdigit(): 
                    # Error!
                    self.abort("Illegal character in number: " + self.curChar)
                while self.peek().isdigit():
                    self.nextChar()

            tokText = self.source[startPos : self.curPos + 1] # Get the substring.
            token = Token(tokText, TokenType.UMBERNAY)

        #Identifier and Keywords
        elif self.curChar.isalpha():
            # Leading character is a letter, so this must be an identifier or a keyword.
            # Get all consecutive alpha numeric characters.
            startPos = self.curPos
            while self.peek().isalnum():
                self.nextChar()

            # Check if the token is in the list of keywords.
            tokText = self.source[startPos : self.curPos + 1] # Get the substring.
            keyword = Token.checkIfKeyword(tokText)
            if keyword == None: # Identifier
                token = Token(tokText, TokenType.IDENTYAY)
            else:   # Keyword
                token = Token(tokText, keyword)

        #Newline
        elif self.curChar == '\n':
            token = Token(self.curChar, TokenType.EWLINENAY)

        #End of File
        elif self.curChar == '\0':
            token = Token('', TokenType.EOF)
        else:
            # Unknown token!
            self.abort("Unknown token: " + self.curChar)
			
        self.nextChar()
        return token

class TokenType(enum.Enum):
	EOF = -1
	EWLINENAY = 0       #NEWLINE
	UMBERNAY = 1        #NUMBER
	IDENTYAY = 2        #IDENT
	INGSTRAY = 3        #STRING
	# Keywords.
	INTPRAY = 101       #PRINT
	INPUTYAY = 102      #INPUT
	ETLAY = 103         #LET
	IFYAY = 104         #IF
	ENTHAY = 105        #THEN
	ENDIFYAY = 106      #ENDIF
	ELSEYAY = 107       #ELSE
	UETRAY = 108        #TRUE
	ALSEFAY = 109       #FALSE
	INTYAY = 110        #FALSE
    # Operators.
	EQUALYAY = 201      #=
	USPLAY = 202        #+
	INUSMAY = 203       #-
	ARSTAY = 204        #*
	ASHSLAY = 205       #/
	EQEQUALYAY = 206    #==
	UPYAY = 207         #++
	OWNDAY = 208        #--
    # Comparators.
	OTEQUALNAY = 209    #!=
	ESSLAY = 210        #<
	EQESSLAY = 211      #<=
	EATERGRAY = 212     #>
	EQEATERGRAY = 213   #>=
    # Parentheses.
	OPENYAY_PAR = 214   #(
	OSECLAY_PAR = 215   #)
    