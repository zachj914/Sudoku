import pygame
import Sudoku_Solver
import time
import random
import copy
pygame.init()
pygame.key.set_repeat(120)
width, height = 1080, 773
display = pygame.display.set_mode((width, height))
pygame.display.set_caption('Sudoku')


class Grid(Sudoku_Solver.Board):
    def __init__(self, values):
        '''Loads an image of the board and a rectangle representing it'''
        Sudoku_Solver.Board.__init__(self, values)
        self.solved = Sudoku_Solver.Board(copy.deepcopy(self.values))
        self.solved = next(self.solved.solve())
        self.full = False
        self.notes = False
        self.note_values = {(y, x): set() for y in range(9) for x in range(9)}
        self.board = pygame.image.load('Images\\Board.png').convert_alpha()
        self.timer = pygame.image.load('Images\\Timer.png').convert_alpha()
        self.board_rect = pygame.Rect(width //
                                      2 - self.board.get_width() // 2,
                                      height //
                                      2 - self.board.get_height() // 2,
                                      self.board.get_width(),
                                      self.board.get_height())
        self.timer_rect = pygame.Rect(width //
                                      2 - self.timer.get_width() // 2,
                                      self.board_rect.top -
                                      self.timer.get_height() + 17,
                                      self.timer.get_width(),
                                      self.timer.get_height())
        self.starting_values = set()
        self.past_moves = []
        for y in range(9):
            for x in range(9):
                if self.values[y][x] != 0:
                    self.starting_values.add((y, x))
        self.errors = set()
        self.active_square = None
        self.digit_pics = {i: pygame.image.load('Images\\' +str(i)+ '.png')
                           .convert_alpha() for i in range(10)}
        self.user_digit_pics = {i: pygame.image.load('Images\\User_'+str(i)+'.png')
                                .convert_alpha() for i in range(1, 10)}
        self.error_digit_pics = {i: pygame.image.load('Images\\Error_'+str(i)+'.png')
                                 .convert_alpha() for i in range(1, 10)}
        self.note_digit_pics = {i: pygame.image.load('Images\\Notes_'+str(i)+'.png')
                                .convert_alpha() for i in range(1, 10)}
        self.highlight_digit_pics = {i: pygame.image.load('Images\\Highlight_' + str(i) + '.png')
                                     .convert_alpha() for i in range(1, 10)}
        self.cursor = pygame.image.load('Images\\Cursor.png').convert_alpha()
        self.active_cursor = pygame.image.load(
            'Images\\Active_Cursor.png').convert_alpha()

    def draw_board(self, play_time):
        '''Draws the board, numbers, and cursor onto the screen'''
        display.blit(self.timer, (self.timer_rect.left, self.timer_rect.top))
        display.blit(self.board, (self.board_rect.left, self.board_rect.top))
        display.blit(self.digit_pics[play_time[0] // 10],
                     (self.timer_rect.left + 23, self.timer_rect.top + 28))
        display.blit(self.digit_pics[play_time[0] - (play_time[0] // 10) * 10],
                     (self.timer_rect.left + 82, self.timer_rect.top + 28))
        display.blit(self.digit_pics[play_time[1] // 10],
                     (self.timer_rect.left + 141, self.timer_rect.top + 28))
        display.blit(self.digit_pics[play_time[1] - (play_time[1] // 10) * 10],
                     (self.timer_rect.left + 200, self.timer_rect.top + 28))
        for row_count, row in enumerate(self.values):
            for num_count, num in enumerate(row):
                if num != 0:
                    if self.active_square is not None and\
                            num == self.values[self.active_square[1]][self.active_square[0]]:
                        digit = self.highlight_digit_pics[num]
                    elif (row_count, num_count) in self.starting_values:
                        digit = self.digit_pics[num]
                    elif (row_count, num_count) in self.errors:
                        digit = self.error_digit_pics[num]
                    else:
                        digit = self.user_digit_pics[num]
                    self.draw_square(digit, (num_count, row_count))
        for cords, notes in self.note_values.items():
            for note in notes:
                self.draw_square(self.note_digit_pics[note], (cords[1], cords[0]))

        square = self.get_square(pygame.mouse.get_pos())
        if square is not None:
            self.draw_square(self.cursor, square)
        if self.active_square is not None:
            self.draw_square(self.active_cursor, self.active_square)

    def get_square(self, mouse_pos):
        if not self.board_rect.collidepoint(mouse_pos):
            return None
        mouse_pos = (mouse_pos[0] - self.board_rect.left,
                     mouse_pos[1] - self.board_rect.top)
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
        return (self.board_rect.left + 28 + 59 *
                cords[0] + 14 * (cords[0]//3), self.board_rect.top +
                28 + 59 * cords[1] + 14 * (cords[1] // 3))

    def draw_square(self, image, cords):
        cords = self.get_square_cords(cords)
        display.blit(image, (cords[0], cords[1]))

    def play_square(self, number, undo=False):
        row, column = (self.active_square[1], self.active_square[0])
        if (self.values[row][column] != number or self.note_values[(row, column)])\
                and undo is False:
            if self.note_values[(row, column)]:
                self.past_moves.append(('Note', copy.deepcopy((row, column)),
                                copy.deepcopy(self.note_values[(row, column)])))
            else:
                self.past_moves.append(('Move', copy.deepcopy((row, column)),
                                        copy.deepcopy(self.values[row][column])))
        if (row, column) not in self.starting_values:
            self.note_values[(row, column)] = set()
            self.values[row][column] = number
        self.full = True if 0 not in [i for row in self.values for i in row]\
            else False
        if not self.find_errors() and self.full:
            win_loop()

    def take_note(self, number):
        row, column = (self.active_square[1], self.active_square[0])
        if board.values[row][column] == 0:
            self.past_moves.append(('Note', copy.deepcopy((row, column)),
                                copy.deepcopy(self.note_values[(row, column)])))
            if number == 0:
                self.note_values[(row, column)] = set()
            elif number in self.note_values[(row, column)]:
                self.note_values[(row, column)].discard(number)
            else:
                self.note_values[(row, column)].add(number)
        elif (row, column) not in self.starting_values:
            self.past_moves.append(('Move', copy.deepcopy((row, column)),
                                    copy.deepcopy(self.values[row][column])))
            self.values[row][column] = 0


    def find_errors(self):
        self.errors = set()
        for y in range(9):
            for x in range(9):
                if (y, x) not in self.starting_values:
                    value = self.values[y][x]
                    self.values[y][x] = 0
                    if not self.check_move((y, x), value):
                        self.errors.add((y, x))
                    self.values[y][x] = value
        return True if len(self.errors) != 0 else False

    def hint(self):
        y, x = random.randint(0, 8), random.randint(0, 8)
        while board.values[y][x] != 0:
            y, x = random.randint(0, 8), random.randint(0, 8)
        board.active_square = [x, y]
        board.play_square(board.solved.values[y][x], undo = True)
        board.starting_values.add((y, x))

    def undo(self):
        try:
            target = self.past_moves.pop()
            if (target[1][0], target[1][1]) not in self.starting_values:
                if target[0] == 'Move':
                    self.active_square = (target[1][1], target[1][0])
                    self.play_square(target[2], undo=True)
                elif target[0] == 'Note':
                    self.active_square = (target[1][1], target[1][0])
                    self.values[target[1][0]][target[1][1]] = 0
                    self.note_values[(target[1][0], target[1][1])] = target[2]
                    self.find_errors()
        except IndexError:
            pass


class Button:
    def __init__(self, image, left_corner=(None, None), horz_alignment=None,
                 vert_alignment=None):
        self.image = image
        self.left_corner = list(left_corner)
        if self.left_corner[0] is None:
            self.left_corner[0] = int(width*horz_alignment\
                - self.image.get_width()/2)
        if self.left_corner[1] is None:
            self.left_corner[1] = int(height*vert_alignment\
                - self.image.get_height()/2)
        self.rect = pygame.Rect(self.left_corner[0], self.left_corner[1],
                                self.image.get_width(),
                                self.image.get_height())
        self.active_image = pygame.transform.scale(
            self.image, (int(self.rect.width * 1.1),
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
    
    def change(self, item_changed, replacement):
        if type(item_changed) == Button:
            self.buttons.discard(item_changed)
            self.buttons.add(replacement)
        else:
            self.background = replacement

    def draw(self, active_buttons):
        display.blit(self.background, (0, 0))
        for button in self.buttons:
            if button in active_buttons:
                button.draw_active()
            else:
                button.draw()


def title_loop():
    running = True
    play_button = Button(pygame.image.load('Images\\PlayText.png').convert_alpha(),
                         horz_alignment=1/2, vert_alignment=7/8)
    options_button = Button(pygame.image.load('Images\\Options.png').convert_alpha(),
                            horz_alignment=1/5, vert_alignment=7/8)
    leaderboard_button = Button(pygame.image.load(
                                'Images\\Leaderboard.png').convert_alpha(),
                                horz_alignment=4/5, vert_alignment=7/8)
    screen = Screens('Images\\Titlescreen.jpg', {play_button, options_button,
                                         leaderboard_button})
    loading = pygame.image.load('Images\\Loading.jpg').convert()
    active_buttons = set()
    screen.draw(active_buttons)
    pygame.display.flip()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if play_button.rect.collidepoint(mouse):
                    display.blit(loading, (0,0))
                    pygame.display.flip()
                    global board
                    board = Grid(Sudoku_Solver.generate_board(5).values)
                    play_loop()
                    running = False
                if options_button.rect.collidepoint(mouse):
                    options_loop()

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


def options_loop():
    screen = Screens('Images\\Options.jpg', set())
    running = True
    screen.draw(set())
    pygame.display.flip()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit(0)


def play_loop():
    notes_button_off = Button(pygame.image.load('Images\\Notes.png'), horz_alignment=7/8,
                          vert_alignment=1/5)
    notes_button_on = Button(pygame.image.load('Images\\Notes_On.png'), horz_alignment=7/8,
                             vert_alignment=1/5)
    notes_button = notes_button_off
    hint_button = Button(pygame.image.load('Images\\Hint.png'), horz_alignment=1/8,
                         vert_alignment=1/5)
    undo_button = Button(pygame.image.load('Images\\Undo.png'), horz_alignment=1/8,
                         vert_alignment=2/5)
    num_keys = {pygame.K_DELETE: 0, pygame.K_BACKSPACE: 0, pygame.K_0: 0, pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3,
                pygame.K_4: 4, pygame.K_5: 5, pygame.K_6: 6, pygame.K_7: 7,
                pygame.K_8: 8, pygame.K_9: 9}
    arrow_keys = {pygame.K_UP: (1, -1),
                  pygame.K_DOWN: (1, 1),
                  pygame.K_LEFT: (0, -1),
                  pygame.K_RIGHT: (0, 1)}
    screen = Screens('Images\\Background.jpg', {hint_button, notes_button, undo_button})
    running = True
    start = time.time()
    active_buttons = set()
    presses = pygame.key.get_pressed()
    while running:
        current = time.time()
        play_time = time.strftime('%M%S', time.gmtime(current-start))
        play_time = (int(play_time[0:2]), int(play_time[2:]))
        screen.draw(active_buttons)
        board.draw_board(play_time)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                raise SystemExit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if board.get_square(mouse) is not None:
                    board.active_square = board.get_square(mouse)
                if hint_button.rect.collidepoint(mouse) and not board.full:
                    board.hint()
                if notes_button.rect.collidepoint(mouse):
                    if notes_button_off in screen.buttons:
                        screen.change(notes_button_off, notes_button_on)
                        board.notes = True
                    else:
                        screen.change(notes_button_on, notes_button_off)
                        board.notes = False
                if undo_button.rect.collidepoint(mouse):
                    board.undo()
            if event.type == pygame.KEYDOWN:
                presses = pygame.key.get_pressed()
                if board.active_square is not None:
                    for key in arrow_keys.keys():
                        if presses[key] == 1:
                            current_square = copy.deepcopy(board.active_square)
                            board.active_square[arrow_keys[key][0]] += arrow_keys[key][1]
                        if not board.board_rect.collidepoint(board.get_square_cords(
                                                                board.active_square)):
                            board.active_square = current_square
                if presses[pygame.K_TAB] == 1:
                    if notes_button_off in screen.buttons:
                        screen.change(notes_button_off, notes_button_on)
                        board.notes = True
                    else:
                        screen.change(notes_button_on, notes_button_off)
                        board.notes = False
            if event.type == pygame.KEYUP:
                if board.active_square is not None:
                    if event.key in num_keys.keys():
                        if board.notes:
                            board.take_note(num_keys[event.key])
                        else:
                            board.play_square(num_keys[event.key])
        mouse = pygame.mouse.get_pos()
        active_buttons = set()
        for button in screen.buttons:
            if button.rect.collidepoint(mouse):
                active_buttons.add(button)
        pygame.time.Clock().tick(30)


def win_loop():
    screen = Screens('Images\\WinScreen.jpg', set())
    running = True
    screen.draw(set())
    pygame.display.flip()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit(0)

title_loop()
