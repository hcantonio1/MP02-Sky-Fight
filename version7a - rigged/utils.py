import math
import pyglet
from pyglet.window import key

import resources


class Button:
    def __init__(self, x, y, text_size_tuple):
        # button constants
        idle_button = pyglet.sprite.Sprite(resources.idle_button, x = x, y = y)
        clicked_button = pyglet.sprite.Sprite(resources.clicked_button, x = x, y = y)
        label = pyglet.text.Label(text = text_size_tuple[0], font_name='ethnocentric rg', font_size = text_size_tuple[1], x = x, y = y, anchor_x = 'center', anchor_y = 'center')

        self.x = x
        self.y = y
        self.sprites = [idle_button, clicked_button]
        self.sprite = self.sprites[0]
        self.width = self.sprite.width
        self.height = self.sprite.height
        self.label = label


    def draw(self):
        self.sprite.draw()
        self.label.draw()


    def is_on(self, tx, ty):
        return abs(self.x - tx) < self.width//2 and abs(self.y - ty) < self.height//2


    def on_click(self, tx, ty):
        if self.is_on(tx, ty):
            self.func()


    def on_hover(self, tx, ty):
        batch = self.sprite.batch
        self.sprite.batch = None
        if self.is_on(tx, ty):
            self.sprites[1].batch = batch
            self.sprite = self.sprites[1]
        else:
            self.sprites[0].batch = batch
            self.sprite = self.sprites[0]


############################################################################################################################################


class GameObject:
    def __init__(self, x, y, sprite):
        self.x = x
        self.y = y
        self.velx = 0
        self.vely = 0

        self.sprite = sprite
        self.width = self.sprite.width
        self.height = self.sprite.height
        self.sprite.anchor_x = self.width//2
        self.sprite.anchor_y = self.height//2


    def draw(self):
        self.sprite.draw()


    def update(self, dt):
        self.x += self.velx*dt
        self.y += self.vely*dt
        self.sprite.x = self.x
        self.sprite.y = self.y



class Player(GameObject):
    def __init__(self, x, y, sprite, radius):
        super().__init__(x, y, sprite)
        self.lives = 3
        self.invincibility = 0
        self.hitbox_radius = radius

        self.speed = 600
        self.fire_rate = 1/10
        self.time_elapsed_since_fire = 0


    def update(self, dt, key_handler, bounds = (1024, 768)):
        if key_handler[key.LSHIFT]:
            self.speed = 300
        else:
            self.speed = 600
        if key_handler[key.LEFT] or key_handler[key.A] and self.x > 25:
            self.x -= self.speed*dt
        if key_handler[key.RIGHT] or key_handler[key.D] and self.x < bounds[0] - 25:
            self.x += self.speed*dt
        if key_handler[key.UP] or key_handler[key.W] and self.y < bounds[1] - 25:
            self.y += self.speed*dt
        if key_handler[key.DOWN] or key_handler[key.S] and self.y > 25:
            self.y -= self.speed*dt
        self.sprite.x = self.x
        self.sprite.y = self.y

        # reduce duration of invincibility
        if self.invincibility > 0:
            self.invincibility -= 1
            self.sprite.opacity = 127*(math.sin(self.invincibility) + 1)
        else:
            self.sprite.opacity = 255


    def fire(self, dt, key_handler, tick):
        bullets = []
        if self.lives < 0:
            return bullets

        a = 0
        if key_handler[key.Z] and tick%8 == 0:
            if key_handler[key.LSHIFT]:
                a = 5
            else:
                a = 15
            for i in range(-1,2):
                bullets.append(Bullet(self.x+10*i, self.y, pyglet.sprite.Sprite(resources.player_laser_image, batch = self.sprite.batch), 600, i*a, 0.2, 15))

        return bullets


class Enemy(GameObject):
    def __init__(self, x, y, sprite, radius):
        super().__init__(x, y, sprite)
        self.start_health = 1000
        self.health = self.start_health
        self.hitbox_radius = radius
        self.vely = -1
        self.velx = 0

        self.fire_rate = 1/3
        self.time_elapsed_since_fire = 0
        self.firing_patterns = []
        self.angle_offset = 0


    def update(self, dt):
        self.velx = 10*math.sin(self.sprite.y/10)
        self.x += self.velx*dt
        self.y += self.vely*dt
        self.sprite.x = self.x
        self.sprite.y = self.y

        hp = self.health
        # enemy wrecks havoc when hp is low
        if hp < 1000 and hp > 750:
            self.firing_patterns = [BulletPatterns.enemy_pattern1]
        if hp <= 750 and hp > 350:
            self.firing_patterns = [BulletPatterns.enemy_pattern1, BulletPatterns.enemy_pattern2]
        if hp <= 350:
            self.firing_patterns = [BulletPatterns.enemy_pattern1, BulletPatterns.enemy_pattern2, BulletPatterns.enemy_pattern3]


    def fire(self, dt, player, tick):
        bullets = []
        if self.health <= 0 or player.lives < 0:
            return bullets

        else:
            for pattern in self.firing_patterns:
                bullets.extend(pattern(self, player, dt, tick))

        return bullets


############################################################################################################################################


class Bullet(GameObject):
    def __init__(self, x, y, sprite, vel, rotation, scale, radius):
        rotation = 0 if rotation == None else math.radians(rotation)

        super().__init__(x, y, sprite)
        self.x = x
        self.y = y
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.scale = scale
        self.rotation = rotation
        self.hitbox_radius = radius
        self.sprite.rotation = math.degrees(rotation)
        self.vel = vel
        self.velx = vel*math.cos(math.pi/2 - rotation)
        self.vely = vel*math.sin(math.pi/2 - rotation)


    def update(self, dt):
        self.x += self.velx*dt
        self.y += self.vely*dt
        self.sprite.x = self.x
        self.sprite.y = self.y


    def out_of_bounds(self, bounds = (1024, 768)):
        return self.x < 0 or self.x > bounds[0] or self.y < 0 or self.y > bounds[1]



class BulletPatterns:
    def enemy_pattern1(enemy, player, dt, tick):
        bullets = []
        angle = UtilityFunctions.firing_angle(enemy.x, enemy.y, player.x, player.y)
        if tick%15 == 0:
            for i in range(-3, 4):
                bullets.append(Bullet(enemy.x, enemy.y, pyglet.sprite.Sprite(resources.circle_bullet, batch = enemy.sprite.batch), -250, i*30 + angle - tick/1.5, 1, 6))
                bullets.append(Bullet(enemy.x, enemy.y, pyglet.sprite.Sprite(resources.circle_bullet, batch = enemy.sprite.batch), 250, i*30 + angle - tick/1.5, 1, 6))
        return bullets


    def enemy_pattern2(enemy, player, dt, tick):
        bullets = []
        angle = UtilityFunctions.firing_angle(enemy.x, enemy.y, player.x, player.y)
        if tick%20 == 0:
            for i in range(-6, 7):
                bullets.append(Bullet(enemy.x, enemy.y, pyglet.sprite.Sprite(resources.circle_bullet_white, batch = enemy.sprite.batch), -300, i*15 + angle - tick/2, 1.2, 7))
                bullets.append(Bullet(enemy.x, enemy.y, pyglet.sprite.Sprite(resources.circle_bullet_white, batch = enemy.sprite.batch), 300, i*15 + angle - tick/2, 1.2, 7))
                bullets.append(Bullet(enemy.x, enemy.y, pyglet.sprite.Sprite(resources.oval_bullet, batch = enemy.sprite.batch), -325, i*15 + angle + tick/2, 1.2, 8))
                bullets.append(Bullet(enemy.x, enemy.y, pyglet.sprite.Sprite(resources.oval_bullet, batch = enemy.sprite.batch), 325, i*15 + angle + tick/2, 1.2, 8))
        return bullets


    def enemy_pattern3(enemy, player, dt, tick):
        bullets = []
        angle = UtilityFunctions.firing_angle(enemy.x, enemy.y, player.x, player.y)
        if tick%10 == 0:
            for i in range(-3, 4):
                if i!=0:
                    bullets.append(Bullet(enemy.x - 200, enemy.y, pyglet.sprite.Sprite(resources.oval_bullet, batch = enemy.sprite.batch), -500, i*30 + angle, 1.5, 10))
                    bullets.append(Bullet(enemy.x - 200, enemy.y, pyglet.sprite.Sprite(resources.oval_bullet, batch = enemy.sprite.batch), 500, i*30 + angle, 1.5, 10))
                    bullets.append(Bullet(enemy.x + 200, enemy.y, pyglet.sprite.Sprite(resources.oval_bullet, batch = enemy.sprite.batch), -500, i*30 + angle, 1.5, 10))
                    bullets.append(Bullet(enemy.x + 200, enemy.y, pyglet.sprite.Sprite(resources.oval_bullet, batch = enemy.sprite.batch), 500, i*30 + angle, 1.5, 10))
        return bullets


############################################################################################################################################


class UtilityFunctions:
    def distance(x, y, x2, y2):
        """ Returns the distance between two points """
        dx = x - x2
        dy = y - y2
        return math.sqrt(dx**2 + dy**2)

    def firing_angle(x, y, x2, y2):
        """ Returns the angle between two points """
        return math.degrees(math.atan((x2 - x)/(y2 - y)))

    def create_buttons(x, y, text_size_tuples, y_step=-80):
        """ Buttons in a column """
        buttons = []
        for i in range(len(text_size_tuples)):
            buttons.append(Button(x, y + y_step*i, text_size_tuples[i]))
        return buttons

    def create_title_label(text, x = 512, y = 384, size = 24):
        return pyglet.text.Label(
            text=text,
            x=x, y=y,
            anchor_x='center',
            anchor_y='center',
            font_name='ethnocentric rg',
            font_size=size,
        )


    def create_label(text, x = 512, y = 384, size = 18, anchor_x = 'center', anchor_y = 'center'):
        return pyglet.text.Label(
            text=text,
            x=x, y=y,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
            font_name='ethnocentric rg',
            font_size=size,
        )


    def create_labels(texts, x, y, y_step=50, size = 14, anchor_x = 'center', anchor_y = 'center'):
        """ Labels in a column """
        labels = []
        y_i = y
        for i in range(len(texts)):
            label = UtilityFunctions.create_label(texts[i], x, y_i, size, anchor_x, anchor_y)
            labels.append(label)
            y_i -= y_step
        return labels
