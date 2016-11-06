import copy
import itertools
import time

############################################################
# Section 1: Sudoku
############################################################

def sudoku_cells():
    c = [(i, j) for i in xrange(9) for j in xrange(9)]
    return c

def sudoku_arcs():
    ans = []
    [ans.append(((a, b), (c, d))) for a in xrange(9) for b in xrange(9) for c in xrange(9) for d in xrange(9) if (((a == c) or (b == d) or (a/3 == c/3 and b/3 == d/3)) and not(a == c and b == d))]
    return ans

def read_board(path):
    board = {}
    with open(path, 'r') as p:
        for i, line in enumerate(p):
            for j, x in enumerate(line):
                if (x == "*"):
                    board[(i, j)] = set([1, 2, 3, 4, 5, 6, 7, 8, 9])
                elif (x.isdigit()):
                    board[(i, j)] = set([int(x)])
    return board

class Sudoku(object):

    CELLS = sudoku_cells()
    ARCS = sudoku_arcs()

    def __init__(self, board):
        #board is an array
        self.board = board

    def get_values(self, cell):
        return self.board[cell]

    def remove_inconsistent_values(self, cell1, cell2):
        if ((len(self.get_values(cell2)) > 1) or (len(self.get_values(cell1)) == 1)):
            return False
        for i in self.get_values(cell2):
            if i in self.get_values(cell1):
                self.get_values(cell1).remove(i)
                return True

    def neighbors(self, a, b = {}):
       return [n for n, i in self.ARCS if (i== a and not n == b)]

    def print_board(self):
        s = ""
        count = 0
        for i in self.CELLS:
            if (len(self.get_values(i)) > 1):
                s += "* "
            else:
                s += str(list(self.get_values(i))[0]) + " "
            count += 1
            if count == 9:
                print(s)
                count = 0
                s = ""
        return

    def blank(self):
        x = [i for i in self.CELLS if len(self.get_values(i)) > 1]
        return x

    def number_sol(self):
        count = itertools.count(0)
        [count.next() for i in self.board if len(self.get_values(i)) == 1] 
        return next(count)

    def infer_ac3(self):
        q = []
        [q.append(x) for x in self.ARCS]
        while not len(q) == 0:
            (a, b) = q.pop()
            if self.remove_inconsistent_values(a, b):
                [q.append((n, a)) for n in self.neighbors(a, b)]

    def infer_improved(self):
        n = self.number_sol()
        while not n == 81:
            self.infer_ac3()            
            for i in self.blank():
                box = set()
                x = [j for j in self.neighbors(i) if  ((i[0])/3 == (j[0])/3 and (i[1])/3 == (j[1])/3)]
                b = [box.union(self.get_values(j)) for j in x]
                box = set()
                for j in b:
                    box= box.union(j)
                if (len(self.get_values(i) - box) == 1):
                    self.board[i] = self.get_values(i) - box 
                    break

                row = set()
                y = [j for j in self.neighbors(i) if (i[0] == j[0])]
                r = [row.union(self.get_values(j)) for j in y]
                row = set()
                for j in r:
                    row = row.union(j)
                if (len(self.get_values(i) - row) == 1):
                    self.board[i] = self.get_values(i) - row
                    break

                col = set()
                z = [j for j in self.neighbors(i) if (i[1] == j[1])]
                c = [col.union(self.get_values(j)) for j in z]
                col = set()
                for j in c:
                    col = col.union(j)
                if (len(self.get_values(i) - col) == 1):
                    self.board[i] = self.get_values(i) - col
                    break

            if(n == self.number_sol()):
                return False
            n = self.number_sol()
        return True

    def infer_with_guessing(self):
        start_time = time.time()
        self.infer_improved()
        for i in  self.blank():
            for j in self.get_values(i):
                temp = copy.deepcopy(self)
                temp.board[i] = set([j])
                temp.infer_improved()

                boo = True
                [x for x in [boo and not temp.get_values(a) == temp.get_values(b) for a, b in temp.ARCS]]
                
                if boo:
                    self.board = temp.board
                    if (len(temp.blank()) == 0):
                        print("--- %s seconds ---" % (time.time() - start_time))
                        return True
                    else:
                        self.infer_with_guessing()
        return False
