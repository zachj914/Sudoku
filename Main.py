import pygame
import Sudoku_Solver
pygame.init()
pygame.key.set_repeat(120)
width, height = 1080, 773
display = pygame.display.set_mode((width, height))
pygame.display.set_caption('Sudoku')


class Grid(Sudoku_Solver.Board):
    def __init__(self, values):
        '''Loads an image of the board and a rectangle representing it'''
        Sudoku_Solver.Board.__init__(self, values)
        self.board = pygame.image.load('Board.png').convert_alpha()
        self.board_rect = pygame.Rect(width /
                                      2 - self.board.get_width() / 2,
                                      height /
                                      2 - self.board.get_height() / 2,
                                      self.board.get_width(),
                                      self.board.get_height())
        self.starting_values = set()
        for y, row in enumerate(self.values):
            for x, num in enumerate(row):
                if self.values[y][x] != 0:
                    self.starting_values.add((y, x))
        self.errors = set()
        self.active_square = None
        self.digit_pics = {1: '1.png', 2: '2.png', 3: '3.png', 4: '4.png',
                           5: '5.png', 6: '6.png', 7: '7.png', 8: '8.png',
                           9: '9.png'}
        self.user_digit_pics = {1: 'User_1.png', 2: 'User_2.png',
                                3: 'User_3.png', 4: 'User_4.png',
                                5: 'User_5.png', 6: 'User_6.png',
                                7: 'User_7.png', 8: 'User_8.png',
                                9: 'User_9.png'}
        self.error_digit_pics = {1: 'Error_1.png', 2: 'Error_2.png',
                                 3: 'Error_3.png', 4: 'Error_4.png',
                                 5: 'Error_5.png', 6: 'Error_6.png',
                                 7: 'Error_7.png', 8: 'Error_8.png',
                                 9: 'Error_9.png'}

    def draw_board(self):
        '''Draws the board, numbers, and cursor onto the screen'''
        display.blit(self.board, (self.board_rect.left, self.board_rect.top))
        for row_count, row in enumerate(self.values):
            for num_count, num in enumerate(row):
                if num != 0:
                    if (row_count, num_count) in self.starting_values:
                        digit = pygame.image.load(self.digit_pics[num]).convert_alpha()
                    elif (row_count, num_count) in self.errors:
                        digit = pygame.image.load(self.error_digit_pics[num]).convert_alpha()
                    else:
                        digit = pygame.image.load(self.user_digit_pics[num]).convert_alpha()
                    self.draw_square(digit, (num_count, row_count))

        square = self.get_square(pygame.mouse.get_pos())
        if square is not None:
            self.cursor = pygame.image.load('Cursor.png').convert_alpha()
            self.draw_square(self.cursor, square)
        if self.active_square is not None:
            self.active_cursor = pygame.image.load('Active_Cursor.png').convert_alpha()
            self.draw_square(self.active_cursor, self.active_square)

    def get_square(self, mouse_pos):
        if not self.board_rect.collidepoint(mouse_pos):
            return None
        mouse_pos = (mouse_pos[0] - self.board_rect.left, mouse_pos[1] - self.board_rect.top)
        bar = 14
        x, y = None, None
        for i in range(9):
            bar += 59 if i % 3 == 1 else 66
            if 14 < mouse_pos[0] < bar and x is None:
                x = i
            if 14 < mouse_pos[1] < bar and y is None:
                y = i
        return[x, y] if None not in [x, y] else None

    def get_square_cords(self, cords):
        return (self.board_rect.left + 28 + 59 * cords[0] + 14 * (cords[0]//3),
                self.board_rect.top + 28 + 59 * cords[1] + 14 * (cords[1] // 3))

    def draw_square(self, image, cords):
        cords = self.get_square_cords(cords)
        display.blit(image, (cords[0], cords[1]))

    def play_square(self, number):
        row, column = (self.active_square[1], self.active_square[0])
        if (row, column) not in self.starting_values:
            self.values[row][column] = number
        Sudoku_Solver.Board.__init__(self, self.values)
        if not self.find_errors() and 0 not in self.unpacked:
            win_loop()

    def find_errors(self):
        self.errors = set()
        for y, row in enumerate(self.rows):
            for x, value in enumerate(row):
                group = row.copy()
                group[x] = 0
                if value != 0 and value in group and (y, x) not in self.starting_values:
                    self.errors.add((y, x))
                    print('Row Error', value)
        for x, column in enumerate(self.columns):
            for y, value in enumerate(column):
                group = column.copy()
                group[y] = 0
                if value != 0 and value in group and (y, x) not in self.starting_values:
                    self.errors.add((y, x))
                    print('Column Error', value)
        for num, square in enumerate(self.squares):
            for index, value in enumerate(square):
                y, x = ((num // 3) * 3 + (index // 3), (num % 3) * 3 + (index % 3))
                group = square.copy()
                group[index] = 0
                if value != 0 and value in group and (y, x) not in self.starting_values:
                    self.errors.add((y, x))
                    print('Square Error', value)
        return True if len(self.errors) != 0 else False


class Button:
    def __init__(self, image, left_corner=(None, None), horz_alignment=None,
                 vert_alignment=None):
        self.image = image
        self.left_corner = list(left_corner)
        if self.left_corner[0] is None:
            self.left_corner[0] = int(width*horz_alignment)\
                - self.image.get_width()/2
        if self.left_corner[1] is None:
            self.left_corner[1] = int(height*vert_alignment)\
                - self.image.get_height()/2
        self.rect = pygame.Rect(self.left_corner[0], self.left_corner[1],
                                self.image.get_width(),
                                self.image.get_height())
        self.active_image = pygame.transform.scale(self.image,
                                                   (int(self.rect.width * 1.1),
                                                    int(self.rect.height * 1.1)))
        self.active_rect = self.rect.copy()

        self.active_rect.inflate_ip(int(self.rect.width * .1),
                                    int(self.rect.height * .1))

    def draw(self):
        display.blit(self.image, self.rect)

    def draw_active(self):
        display.blit(self.active_image, self.active_rect)


class Screens:
    def __init__(self, background, buttons):
        self.background = pygame.image.load(background).convert()
        self.buttons = buttons

    def draw(self, active_buttons):
        display.blit(self.background, (0, 0))
        for button in self.buttons:
            if button in active_buttons:
                button.draw_active()
            else:
                button.draw()


def title_loop():
    running = True
    play_button = Button(pygame.image.load('PlayText.png').convert_alpha(),
                         horz_alignment=1/2, vert_alignment=7/8)
    options_button = Button(pygame.image.load('Options.png').convert_alpha(),
                            horz_alignment=1/5, vert_alignment=7/8)
    leaderboard_button = Button(pygame.image.load(
                                'Leaderboard.png').convert_alpha(),
                                horz_alignment=4/5, vert_alignment=7/8)
    screen = Screens('Titlescreen.jpg', {play_button, options_button,
                                         leaderboard_button})
    active_buttons = set()
    screen.draw(active_buttons)
    pygame.display.flip()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if play_button.rect.collidepoint(mouse):
                    play_loop()
                    running = False

        mouse = pygame.mouse.get_pos()
        prev_buttons = set(active_buttons)
        active_buttons = set()
        for button in screen.buttons:
            if button.rect.collidepoint(mouse):
                active_buttons.add(button)
        if active_buttons != prev_buttons:
            screen.draw(active_buttons)
            pygame.display.flip()
    pygame.time.Clock().tick(30)


def play_loop():
    num_keys = {pygame.K_0: 0, pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3,
                pygame.K_4: 4, pygame.K_5: 5, pygame.K_6: 6, pygame.K_7: 7,
                pygame.K_8: 8, pygame.K_9: 9}
    arrow_keys = {pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT}
    screen = Screens('Background.jpg', set())
    running = True
    while running:
        screen.draw(set())
        board.draw_board()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                board.active_square = board.get_square(mouse)
            presses = pygame.key.get_pressed()
            if 1 in presses:
                for key in num_keys.keys():
                    if presses[key] == 1:
                        board.play_square(num_keys[key])
                current_square = board.active_square.copy()
                for key in arrow_keys:
                    if presses[key] == 1:
                        if key == pygame.K_UP:
                            board.active_square[1] -= 1
                        if key == pygame.K_DOWN:
                            board.active_square[1] += 1
                        if key == pygame.K_LEFT:
                            board.active_square[0] -= 1
                        if key == pygame.K_RIGHT:
                            board.active_square[0] += 1
                if not board.board_rect.collidepoint(board.get_square_cords(
                                                     board.active_square)):
                    board.active_square = current_square
        pygame.time.Clock().tick(30)


def win_loop():
    screen = Screens('WinScreen.jpg', set())
    running = True
    screen.draw(set())
    pygame.display.flip()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


board = Grid([[6, 7, 0, 3, 1, 0, 0, 9, 0],
              [0, 0, 3, 0, 0, 4, 2, 0, 5],
              [4, 0, 0, 0, 5, 0, 0, 7, 0],
              [0, 3, 0, 0, 9, 0, 0, 0, 0],
              [0, 0, 0, 5, 0, 6, 0, 0, 0],
              [0, 0, 0, 0, 4, 0, 0, 1, 0],
              [0, 4, 0, 0, 7, 0, 0, 0, 6],
              [9, 0, 7, 2, 0, 0, 4, 0, 0],
              [0, 5, 0, 0, 3, 1, 0, 2, 9]])
title_loop()
