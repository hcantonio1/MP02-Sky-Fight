import pyglet

from utils import Button, UtilityFunctions

class Menu:
    def __init__(self, window):
        self.window = window
        self.center_x, self.center_y = (window.width//2, window.height//2)

        # create menu screens contents
        self.menu_buttons, self.menu_labels = self.create_main_menu()
        self.top_scores_buttons, self.top_scores_labels = self.create_top_scores()
        self.more_menu_buttons, self.more_menu_labels = self.create_more_menu()
        self.pause_menu_buttons, self.pause_menu_labels = self.create_pause_menu()

        # set up batch for the menu
        self.main_menu_first_batch = pyglet.graphics.Batch()
        self.main_menu_second_batch = pyglet.graphics.Batch()
        self.current_batch = dict()
        self.current_batch['buttons'] = self.menu_buttons
        self.current_batch['labels'] = self.menu_labels
        self.current_state = window.state

        # set the initial batch
        for button in self.current_batch['buttons']:
            button.sprite.batch = self.main_menu_first_batch
            button.label.batch = self.main_menu_second_batch
        for label in self.current_batch['labels']:
            label.batch = self.main_menu_second_batch


    def update_batch(self):
        if not self.window.state == self.current_state:
            self.current_state = self.window.state

            # 'unbatch' the current_batch
            for button in self.current_batch['buttons']:
                button.sprite.batch = None
                button.label.batch = None
            for label in self.current_batch['labels']:
                label.batch = None

            # change current_batch
            if self.current_state == self.window.states['MAIN_MENU']:
                self.current_batch['buttons'] = self.menu_buttons
                self.current_batch['labels'] = self.menu_labels
            elif self.current_state == self.window.states['TOP_SCORES']:
                self.current_batch['buttons'] = self.top_scores_buttons
                self.current_batch['labels'] = self.top_scores_labels
            elif self.current_state == self.window.states['MORE_MENU']:
                self.current_batch['buttons'] = self.more_menu_buttons
                self.current_batch['labels'] = self.more_menu_labels
            elif self.current_state == self.window.states['PAUSED']:
                self.current_batch['buttons'] = self.pause_menu_buttons
                self.current_batch['labels'] = self.pause_menu_labels

            # set the batch of current_batch
            if not self.current_state in [self.window.states['PLAYING'], self.window.states['GAME_OVER']]:
                for button in self.current_batch['buttons']:
                    button.sprite.batch = self.main_menu_first_batch
                    button.label.batch = self.main_menu_second_batch
                for label in self.current_batch['labels']:
                    label.batch = self.main_menu_second_batch


    def draw(self):
        self.main_menu_first_batch.draw()
        self.main_menu_second_batch.draw()


    def on_hover(self, x, y, button, modifiers):
        for button in self.current_batch['buttons']:
            button.on_hover(x, y)


    def on_click(self, x, y, button, modifiers):
        for button in self.current_batch['buttons']:
            button.on_click(x, y)


    def create_main_menu(self):
        menu_labels = []
        self.title = UtilityFunctions.create_title_label('Sky Fight', self.center_x, self.center_y + 150, 36)
        menu_labels.append(self.title)

        text_size_tuples_for_each_button = [('PLAY', 18), ('SCORES', 14), ('MORE', 18), ('EXIT', 18)]
        menu_buttons = UtilityFunctions.create_buttons(self.center_x, self.center_y, text_size_tuples_for_each_button)
        return (menu_buttons, menu_labels)


    def create_top_scores(self):
        top_scores_buttons = UtilityFunctions.create_buttons(self.center_x, self.center_y - 240, [('BACK', 18)])
        top_scores_labels = []
        top_scores_labels.append(UtilityFunctions.create_title_label('SCORES', self.center_x, self.center_y + 150))

        # scores.txt contains the top 5 highest scorers of the game
        self.filename = 'scores.txt'
        scores = open(self.filename)
        high_scores = scores.read()
        self.top_scores = []
        self.max_top_scores = 5
        for hs in high_scores.split('\n'):
            hs = hs.split()
            self.top_scores.append([hs[0], hs[1]])
        scores.close()


        y = self.center_y + 80
        x1 = self.center_x - 200
        x2 = self.center_x + 200

        top_scores_labels.extend(UtilityFunctions.create_labels([str(txt[1]) for txt in self.top_scores], x2, y))
        top_scores_labels.extend(UtilityFunctions.create_labels([txt[0] for txt in self.top_scores], x1, y))

        return (top_scores_buttons, top_scores_labels)


    def update_scores(self, scorer, new_score):
        is_highscore = False
        for i in range(len(self.top_scores)):
            if new_score > int(self.top_scores[i][1]):
                self.top_scores.insert(i, [scorer, new_score])
                is_highscore = True
                if len(self.top_scores) > self.max_top_scores:
                    del self.top_scores[self.max_top_scores]
                break

        if is_highscore:
            new_scores = open(self.filename, 'w')
            new_scores.write('\n'.join([hs[0] + ' ' + str(hs[1]) for hs in self.top_scores]))
            new_scores.close()

        self.top_scores_labels = self.create_top_scores()[1]


    def create_more_menu(self):
        more_menu_labels = []

        help_message = '''Control your ship with the arrow keys. Shoot with the 'z' key.\nAlso hold shift to concentrate your bullets at the cost of speed.\nGet the highest score!'''
        credits_message = '''Music: The World Revolving (Deltarune OST) by Toby Fox\nBullet sprites taken from spriters-resource.com'''

        more_menu_labels.append(UtilityFunctions.create_title_label('HELP', self.center_x, self.center_y + 180))
        more_menu_labels.extend(UtilityFunctions.create_labels(help_message.split('\n'), self.center_x, self.center_y + 130))
        more_menu_labels.append(UtilityFunctions.create_title_label('CREDITS', self.center_x, self.center_y - 50))
        more_menu_labels.extend(UtilityFunctions.create_labels(credits_message.split('\n'), self.center_x, self.center_y - 100))

        more_menu_buttons = self.top_scores_buttons
        return (more_menu_buttons, more_menu_labels)


    def create_pause_menu(self):
        pause_menu_labels = []
        pause_menu_labels.append(UtilityFunctions.create_title_label('PAUSED', self.center_x, self.center_y + 150))

        text_size_tuples_for_each_button = [('CONTINUE', 11.5), ('SCORES', 14), ('MORE', 18), ('QUIT', 18)]
        pause_menu_buttons = UtilityFunctions.create_buttons(self.center_x, self.center_y, text_size_tuples_for_each_button)
        pause_menu_buttons.pop(1)
        pause_menu_buttons.pop(1)
        return (pause_menu_buttons, pause_menu_labels)
