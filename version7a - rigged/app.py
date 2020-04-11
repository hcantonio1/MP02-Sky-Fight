import pyglet
from pyglet.window import key

from menu import Menu
from game import Game
import resources


class AppWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.states = {
            'MAIN_MENU': 0,
            'PLAYING': 1,
            'PAUSED': 2,
            'GAME_OVER': 3,
            'TOP_SCORES': 4,
            'MORE_MENU': 5
        }

        self.state = self.states['MAIN_MENU']

        # Key handlers saves the state of the keyboard
        self.key_handler = key.KeyStateHandler()
        self.push_handlers(self.key_handler)

        self.menu = Menu(self)
        self.game = Game(self)

        # assign button functions
        self.menu.menu_buttons[0].func = self.start_game
        self.menu.menu_buttons[1].func = self.show_scores
        self.menu.menu_buttons[2].func = self.show_more
        self.menu.menu_buttons[3].func = self.do_exit
        self.menu.top_scores_buttons[0].func = self.go_back
        self.menu.pause_menu_buttons[0].func = self.continue_game
        self.menu.pause_menu_buttons[1].func = self.quit_game
        self.game.game_hud_buttons[0].func = self.pause_game
        self.game.game_over_buttons[0].func = self.quit_game

        # set up window media player
        self.player = pyglet.media.Player()
        self.player.loop = True
        self.player.queue(resources.music)
        self.player.volume = 0.25
        self.player.play()

        pyglet.clock.schedule_interval(self.update, 1.0 / 120.0)


    def update(self, dt):
        self.menu.update_batch()
        self.game.update(dt)


    def on_draw(self):
        app_window.clear()
        some_x = -425 if app_window.state in [app_window.states['PLAYING'], app_window.states['GAME_OVER']] else 0
        resources.background_image.blit(some_x, 0)
        self.menu.draw()
        self.game.draw()


    def on_mouse_motion(self, x, y, button, modifiers):
        self.menu.on_hover(x, y, button, modifiers)


    def on_mouse_press(self, x, y, button, modifiers):
        self.menu.on_click(x, y, button, modifiers)
        self.game.on_click(x, y, button, modifiers)


    # only button functions follow
    def start_game(self):
        if self.state == self.states['MAIN_MENU']:
            self.state = self.states['PLAYING']

    def show_scores(self):
        if self.state == self.states['MAIN_MENU']:
            self.state = self.states['TOP_SCORES']

    def show_more(self):
        if self.state == self.states['MAIN_MENU']:
            self.state = self.states['MORE_MENU']

    def do_exit(self):
        if self.state == self.states['MAIN_MENU']:
            pyglet.app.exit()

    def go_back(self):
        if self.state in [self.states['TOP_SCORES'], self.states['MORE_MENU']]:
            self.state = self.states['MAIN_MENU']

    def pause_game(self):
        if self.state == self.states['PLAYING']:
            self.state = self.states['PAUSED']

    def continue_game(self):
        if self.state == self.states['PAUSED']:
            self.state = self.states['PLAYING']

    def quit_game(self):
        if self.state in [self.states['PAUSED'], self.states['GAME_OVER']]:

            if self.state == self.states['GAME_OVER']:
                self.menu.update_scores('You', self.game.score)

            # reset game
            self.game = Game(self)
            self.game.game_hud_buttons[0].func = self.pause_game
            self.game.game_over_buttons[0].func = self.quit_game

            # then go back to main menu
            self.state = self.states['MAIN_MENU']


app_window = AppWindow(1024, 768, "Sky Fight")
pyglet.app.run()
