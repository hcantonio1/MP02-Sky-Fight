import pyglet
from pyglet.window import key
from utils import Player, Enemy, Bullet, UtilityFunctions
import resources


class Game:
    def __init__(self, window):
        self.window = window
        self.center_x, self.center_y = (window.width//2, window.height//2)
        self.key_handler = self.window.key_handler

        # create the elements of the game
        self.player, self.enemy = self.create_player_enemy()
        self.players = [self.player]
        self.enemies = [self.enemy]
        self.player_bullets = []
        self.enemy_bullets = []

        # hud for heads up display
        self.game_hud_labels, self.game_hud_buttons = self.create_game_hud()
        self.game_over_labels, self.game_over_buttons = self.create_game_over_screen()

        # set up batch for the game
        self.game_batch = pyglet.graphics.Batch()
        self.current_batch = dict()
        self.current_batch['player'] = [self.player]
        self.current_batch['enemies'] = [self.enemy]
        self.current_batch['player_bullets'] = []
        self.current_batch['enemy_bullets'] = []
        self.current_batch['labels'] = self.game_hud_labels
        self.current_batch['buttons'] = self.game_hud_buttons
        self.current_state = self.window.state

        # set up tick control and bonus
        self.tick_counter = 0
        self.score_timebonus = 750000


    def check_collision(self):

        # when player bullets hit the enemy
        for bullet in self.player_bullets:
            if UtilityFunctions.distance(bullet.x, bullet.y, self.enemy.x, self.enemy.y) < (bullet.hitbox_radius + self.enemy.hitbox_radius) and self.enemy in self.enemies:
                self.enemy.health -= 1
                self.player_bullets.remove(bullet)
                self.score += 3000
                if self.enemy.health < 250:
                    resources.damage.play()
                if self.enemy.health <= 0:
                    self.enemies.remove(self.enemy)
                    #self.score += round(self.score_timebonus)
                    resources.defeat_sound.play()
                    self.player.invincibility = 1200
                    break

        # when enemy bullets hit the player
        for bullet in self.enemy_bullets:
            if UtilityFunctions.distance(bullet.x, bullet.y, self.player.x, self.player.y) < (bullet.hitbox_radius + self.player.hitbox_radius) and self.player.invincibility == 0:
                self.player.lives -= 1
                self.enemy_bullets.remove(bullet)
                resources.death_sound.play()
                self.player.invincibility = 300
                #self.score -= 250000
                self.player.x = self.center_x*3/4
                self.player.y = self.center_y//3
                break
            if UtilityFunctions.distance(bullet.x, bullet.y, self.player.x, self.player.y) < 50:
                self.score += 25


    def update(self, dt):
        self.update_batch()
        if self.current_state == self.window.states['PLAYING']:

            self.tick_counter += 1
            self.score_timebonus -= 75

            # write on the game hud
            some_label = 'player: dead' if self.player.lives < 0 else 'PLAYER LIVES:' + str(self.player.lives)
            self.game_hud_labels[0].text = 'ENEMY HP: ' + str(self.enemy.health)
            self.game_hud_labels[1].text = 'LEVEL: ' + str(self.level)
            self.game_hud_labels[2].text = some_label
            self.game_hud_labels[3].text = 'SCORE: ' + str(self.score)

            # update player and enemy and bullets
            for player in self.players:
                player.update(dt, self.key_handler, (0.75*self.window.width, self.window.height))
            for enemy in self.enemies:
                enemy.update(dt)                # the only enemy
            for bullet in self.player_bullets:
                bullet.update(dt)
                if bullet.out_of_bounds((0.75*self.window.width, self.window.height)):
                    self.player_bullets.remove(bullet)
            for bullet in self.enemy_bullets:
                bullet.update(dt)
                if bullet.out_of_bounds((0.75*self.window.width, self.window.height)):
                    self.enemy_bullets.remove(bullet)

            # alive player or enemy will fire bullets
            for player in self.players:
                self.player_bullets.extend(player.fire(dt, self.key_handler, self.tick_counter))
            for enemy in self.enemies:
                self.enemy_bullets.extend(enemy.fire(dt, self.player, self.tick_counter))

            if len(self.enemy.fire(dt, self.player, self.tick_counter)) > 0:
                resources.enemy_attack.play()

            self.check_collision()

            # check game over
            if (len(self.enemies) < 1 or self.player.lives < 0) and len(self.enemy_bullets) < 1:
                self.window.state = self.window.states['GAME_OVER']


    def update_batch(self):
        if not self.window.state == self.current_state:
            self.current_state = self.window.state

            # 'unbatch' the current_batch
            self.player.sprite.batch = None
            for enemy in self.current_batch['enemies']:
                enemy.sprite.batch = None
            for label in self.current_batch['labels']:
                label.batch = None
            for button in self.current_batch['buttons']:
                button.label.batch = None

            # change current_batch
            if self.current_state == self.window.states['PLAYING']:
                self.current_batch['player'] = [self.player]
                self.current_batch['enemies'] = self.enemies
                self.current_batch['labels'] = self.game_hud_labels
                self.current_batch['buttons'] = self.game_hud_buttons
            if self.current_state == self.window.states['GAME_OVER']:
                if self.enemy.health <=0:
                    self.score += round(self.score_timebonus)
                self.game_over_labels[0].text = 'You win!' if self.enemy.health <= 0 else 'You lost'
                self.game_over_labels[1].text = 'Your score ' + str(self.score - self.score_timebonus - self.player.lives*250000) + f' timebonus {self.score_timebonus} + lives {self.player.lives}*250000' if self.enemy.health <= 0 else f'Your Score: {self.score}'
                self.game_over_labels[2].text = f'Final Score: {self.score}' if self.enemy.health <= 0 else ''


                self.current_batch['player'] = []
                self.current_batch['enemies'] = self.enemies
                self.current_batch['labels'] = self.game_hud_labels + self.game_over_labels
                self.current_batch['buttons'] = self.game_over_buttons

            # set the batch of current_batch
            if self.current_state in [self.window.states['PLAYING'], self.window.states['GAME_OVER']]:
                self.player.sprite.batch = self.game_batch
                for enemy in self.current_batch['enemies']:
                    enemy.sprite.batch = self.game_batch
                for label in self.current_batch['labels']:
                    label.batch = self.game_batch
                for button in self.current_batch['buttons']:
                    button.label.batch = self.game_batch


    def draw(self):
        self.game_batch.draw()


    def on_click(self, x, y, button, modifiers):
        for button in self.current_batch['buttons']:
            button.on_click(x, y)


    def create_game_hud(self):
        self.level = 9999
        self.score = 0
        enemy_hp = pyglet.text.Label('', font_name='ethnocentric rg', x = 800, y = self.window.height - 15, anchor_y='top')
        level = pyglet.text.Label('', font_name='ethnocentric rg', x = 800, y = self.window.height - 45, anchor_y='top')
        player_hp = pyglet.text.Label('', font_name='ethnocentric rg', x = 800, y = self.window.height - 75, anchor_y='top')
        score = pyglet.text.Label('', font_name='ethnocentric rg', x = 800, y = self.window.height - 105, anchor_y='top')
        pause_button = UtilityFunctions.create_buttons(self.window.width - 15, 15, [('PAUSE', 16)])[0]
        pause_button.label.anchor_y = 'bottom'
        pause_button.label.anchor_x = 'right'
        return ([enemy_hp, level, player_hp, score], [pause_button])


    def create_player_enemy(self):
        self.player = Player(self.center_x*3/4, self.center_y//3, resources.player_image_sprite, 5)
        self.enemy = Enemy(self.center_x*3/4, 7*self.center_y//4, resources.enemy_image_sprite, 50)
        return (self.player, self.enemy)


    def create_game_over_screen(self):
        win_text = pyglet.text.Label('', font_name='ethnocentric rg', font_size = 18, x = self.center_x, y = self.center_y, anchor_x='center', anchor_y='center')
        bonus_text = pyglet.text.Label('', font_name='ethnocentric rg', font_size = 14, x = self.center_x, y = self.center_y - 50, anchor_x='center', anchor_y='center')
        final_score = pyglet.text.Label('', font_name='ethnocentric rg', font_size = 24, x = self.center_x, y = self.center_y - 100, anchor_x='center', anchor_y='center')
        exit_button = UtilityFunctions.create_buttons(self.window.width - 15, 15, [('EXIT', 18)])[0]
        exit_button.label.anchor_y = 'bottom'
        exit_button.label.anchor_x = 'right'
        return ([win_text, bonus_text, final_score], [exit_button])
