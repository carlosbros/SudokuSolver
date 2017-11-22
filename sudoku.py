############################################################
# Sudoku Solver
############################################################

import Queue


def same_row(y_1, y_2):
    return y_1 == y_2


def same_col(x_1, x_2):
    return x_1 == x_2


def same_block((y_1, x_1), (y_2, x_2)):
    return y_1 // 3 == y_2 // 3 and x_1 // 3 == x_2 // 3


def sudoku_cells():
    return [(i, j) for i in xrange(9) for j in xrange(9)]


def sudoku_arcs():
    return [((y_1, x_1), (y_2, x_2)) for (y_1, x_1) in sudoku_cells()
            for (y_2, x_2) in sudoku_cells() if (y_1 == y_2 or x_1 == x_2 or
            same_block((y_1, x_1), (y_2, x_2)))]


def read_board(path):
    board_map = {}
    with open(path) as f:
        sudoku = f.readlines()
    i = 0
    for row in sudoku:
        for j in xrange(9):
            entry = row[j]
            coordinate = (i, j)
            if entry == "*":
                board_map[coordinate] = set([k + 1 for k in xrange(9)])
            else:
                board_map[coordinate] = set([int(entry)])
        i += 1
    return board_map


class Sudoku(object):

    CELLS = sudoku_cells()
    ARCS = sudoku_arcs()

    def __init__(self, board):
        self.board = board

    def get_values(self, cell):
        return self.board[cell]

    def get_neighbors(self, cell):
        return [x for x in self.CELLS if self.is_neighbor(cell, x)]

    def get_row(self, cell):
        return [x for x in self.CELLS if same_row(x[1], cell[1]) and cell != x]

    def get_col(self, cell):
        return [x for x in self.CELLS if same_col(x[0], cell[0]) and cell != x]

    def get_block(self, cell):
        return [x for x in self.CELLS if same_block(x, cell) and cell != x]

    def is_neighbor(self, cell1, cell2):
        return (same_row(cell1[1], cell2[1]) or same_col(cell1[0], cell2[0])
                or same_block(cell1, cell2)) and cell1 != cell2

    def remove_inconsistent_values(self, cell1, cell2):
        if self.is_neighbor(cell1, cell2):
            if len(self.board[cell1]) == 1 and len(self.board[cell2]) != 1:
                for x in self.board[cell1]:
                    if x not in self.board[cell2]:
                        return False
                    self.board[cell2].remove(x)
                return True
            elif len(self.board[cell2]) == 1 and len(self.board[cell1]) != 1:
                for x in self.board[cell2]:
                    if x not in self.board[cell1]:
                        return False
                    self.board[cell1].remove(x)
                return True
        return False

    def is_solved(self):
        for cell in self.CELLS:
            if len(self.board[cell]) > 1:
                return False
        return True

    def infer_ac3(self):
        q = Queue.Queue()
        for arc in self.ARCS:
            q.put(arc)
        while not q.empty():
            (x1, x2) = q.get()
            if self.remove_inconsistent_values(x1, x2):
                for cell in self.get_neighbors(x1):
                    if cell != x2:
                        q.put((cell, x1))

    def run_improvement(self):
        changed = False
        for cell in self.CELLS:
            if len(self.board[cell]) > 1:
                done = False
                if not done:
                    cell_vals = list(self.board[cell])
                    for row_n in self.get_row(cell):
                        for val in self.board[row_n]:
                            if val in cell_vals:
                                cell_vals.remove(val)
                    if len(cell_vals) == 1:
                        self.board[cell] = set(cell_vals)
                        done = True
                        changed = True
                if not done:
                    cell_vals = list(self.board[cell])
                    for col_n in self.get_col(cell):
                        for val in self.board[col_n]:
                            if val in cell_vals:
                                cell_vals.remove(val)
                    if len(cell_vals) == 1:
                        self.board[cell] = set(cell_vals)
                        done = True
                        changed = True
                if not done:
                    for block_n in self.get_block(cell):
                        for val in self.board[block_n]:
                            if val in cell_vals:
                                cell_vals.remove(val)
                    if len(cell_vals) == 1:
                        self.board[cell] = set(cell_vals)
                        done = True
                        changed = True
        return changed

    def infer_improved(self):
        self.infer_ac3()
        while self.run_improvement():
            self.infer_ac3()

    def invalid_guess(self, cell):
        for neighbor in self.get_neighbors(cell):
            if len(self.board[neighbor]) == 1:
                cell_val = self.board[cell].pop()
                self.board[cell].add(cell_val)
                n_val = self.board[neighbor].pop()
                self.board[neighbor].add(n_val)
                if cell_val == n_val:
                    return True
        return False

    def unsolvable(self):
        for cell in self.CELLS:
            if len(self.board[cell]) == 0:
                return True
        return False

    def guess_cell_value(self, cell):
        values = list(self.board[cell])
        for val in values:
            self.board[cell] = set([val])
            if not self.invalid_guess(cell):
                guess_is_valid = True
                for neighbor in self.get_neighbors(cell):
                    if len(self.board[neighbor]) > 1:
                        if not self.guess_cell_value(neighbor):
                            guess_is_valid = False
                            break
                if guess_is_valid:
                    return True
        # If the code gets here, unsolvable board, so set original vals back
        self.board[cell] = set(values)
        return False

    def infer_with_guessing(self):
        cells = [(i, j) for (i, j) in self.CELLS]
        while not self.is_solved():
            next_cell = cells.pop()
            if len(self.board[next_cell]) > 1:
                if self.guess_cell_value(next_cell):
                    self.infer_improved()

