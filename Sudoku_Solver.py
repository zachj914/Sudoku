import random
import copy
import cProfile


class Board:
    def __init__(self, values):
        self.values = values

    def __repr__(self):
        output = "\n"
        for num, row in enumerate(self.values):
            if num % 3 == 0:
                output += "-------------------------\n"
            for num, value in enumerate(row):
                if num % 3 == 0:
                    output += '| '
                output += str(value) + ' '
            output += '|\n'
        output += "-------------------------\n"
        return output

    def check_move(self, index, value):
        '''Checks for conflicting numbers in indexed cell's
        row, column, and square'''
        if value not in self.values[index[0]] and value not in\
            [i[index[1]] for i in self.values] and value not in\
                [self.values[(index[0]//3)*3+a][(index[1]//3)*3+b]
                 for a in range(3) for b in range(3)]:
            return True
        else:
            return False

    def solve(self):
        '''Recursively guesses and backtracks until a solved board is found'''
        for y in range(9):
            for x in range(9):
                if self.values[y][x] == 0:
                    rand_val = random.randint(1, 9)
                    for i in range(1, 10):
                        i = (i + rand_val) % 9 + 1
                        if self.check_move((y, x), i):
                            self.values[y][x] = i
                            for solution in self.solve():
                                yield solution
                            self.values[y][x] = 0
                    return
        yield self


def generate_board(fails):
    '''Creates a random fully solved board and removes spaces that don't
    result in multiple solutions until the specified number of fails is hit'''
    board = Board([[0 for i in range(9)] for j in range(9)])
    board = next(board.solve())
    i = 0
    while i <= fails:
        y, x = random.randint(0, 8), random.randint(0, 8)
        while board.values[y][x] == 0:
            y, x = random.randint(0, 8), random.randint(0, 8)
        cell_copy = copy.deepcopy(board.values[y][x])
        board.values[y][x] = 0
        board_copy = Board(copy.deepcopy(board.values))
        solutions = board_copy.solve()
        try:
            next(solutions)
            next(solutions)
            board.values[y][x] = cell_copy
            i += 1
        except StopIteration:
            pass
    return board


def main():
    board = Board([[0, 0, 0, 6, 0, 0, 8, 3, 0],
                   [0, 0, 4, 3, 0, 0, 1, 0, 0],
                   [0, 9, 0, 0, 0, 2, 0, 0, 5],
                   [0, 7, 0, 0, 3, 5, 0, 0, 0],
                   [0, 4, 0, 0, 0, 8, 6, 0, 0],
                   [0, 0, 1, 0, 4, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 7, 8],
                   [0, 0, 0, 0, 0, 0, 4, 2, 0],
                   [9, 0, 0, 0, 0, 0, 0, 6, 0]])
    for solution in board.solve():
        print(solution)


if __name__ == '__main__':
    main()
