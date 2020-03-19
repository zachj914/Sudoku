import random

class Board:
    def __init__(self, values):
        self.values = values
        self.rows = [row for row in self.values]
        self.columns = [[self.values[i][j]
                        for i in range(9)] for j in range(9)]
        self.squares = [[self.values[i+a][j+b]
                        for a in range(3) for b in range(3)]
                        for i in [0, 3, 6] for j in [0, 3, 6]]
        self.unpacked = []
        for row in self.values:
            self.unpacked.extend(row)

    def __repr__(self):
        output = ""
        for num, row in enumerate(self.rows):
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
        return True if check_member(index[0], value, self.columns[index[1]]) and\
               check_member(index[1], value, self.rows[index[0]]) and\
               check_member(((index[0] % 3) * 3 + (index[1] % 3)), value, self.squares[(index[0] // 3) * 3 + (index[1] // 3)])\
               else False

    def solve(self):
        global output
        if 0 not in self.unpacked:
            output.append(self)
            print(output)
            return True, output
        for y in range(9):
            for x in range(9):
                if self.values[y][x] == 0:
                    for i in range(1, 10):
                        if self.check_move((y, x), i):
                            self.values[y][x] = i
                            self.__init__(self.values)
                            self.solve()
                            self.values[y][x] = 0
                            self.__init__(self.values)
                    return False, output


def check_member(index, value, container):
    if container[index] != 0:
        raise ValueError("Target is a nonzero value:")
    return True if value not in container else False


def generate_board():
    board = Board([[0 for i in range(9)] for j in range(9)])
    print(board.solve())


def main():
    board = Board([[6, 7, 0, 3, 1, 0, 0, 9, 0],
                  [0, 0, 3, 0, 0, 4, 2, 0, 5],
                  [4, 0, 0, 0, 5, 0, 0, 7, 0],
                  [0, 3, 0, 0, 9, 0, 0, 0, 0],
                  [0, 0, 0, 5, 0, 6, 0, 0, 0],
                  [0, 0, 0, 0, 4, 0, 0, 1, 0],
                  [0, 4, 0, 0, 7, 0, 0, 0, 6],
                  [9, 0, 7, 2, 0, 0, 4, 0, 0],
                  [0, 5, 0, 0, 3, 1, 0, 2, 9]])
    output = []
    print(board.solve())


if __name__ == '__main__':
    main()
