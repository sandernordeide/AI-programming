class Cell:



    def __init__(self, board, row, column):
        self.board = board #the board of cells
        self.row = row #row position in board
        self.column = column #column position in board
        self.state = 1 # States 0: empty, 1: peg,
                       # 2: peg jumped to cell, 3: peg jumped from cell, -1: dummy cell

    def setDummy(self):
        self.state = -1

    def removePeg(self):
        self.state = 0

    def placePeg(self):
        self.state = 1

    def jumpedTo(self):
        self.state = 2

    def jumpedFrom(self):
        self.state = 3

    def isEmpty(self):
        return self.state == 0 or self.state == 3

    def getRow(self):
        return self.row

    def getColumn(self):
        return self.column

    def getState(self):
        return self.state

    def __repr__(self):
        return "("+ str(self.getRow()) + "," + str(self.getColumn()) + ")"