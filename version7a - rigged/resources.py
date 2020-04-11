import pyglet


def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width//2
    image.anchor_y = image.height//2


background_image = pyglet.resource.image('res/space.jpg')


# buttons
idle_button = pyglet.resource.image('res/button0.png')
center_image(idle_button)

clicked_button = pyglet.resource.image('res/button1.png')
center_image(clicked_button)


# ships
player_image = pyglet.resource.image('res/ship.png')
center_image(player_image)
player_image_sprite = pyglet.sprite.Sprite(player_image)
player_image_sprite.scale = 0.3

enemy_image = pyglet.resource.image('res/ship.png')
center_image(enemy_image)
enemy_image_sprite = pyglet.sprite.Sprite(enemy_image)
enemy_image_sprite.scale = 0.8
enemy_image_sprite.rotation = 180


#bullets
player_laser_image = pyglet.resource.image('res/player_bullet.png')
center_image(player_laser_image)
player_laser_image_sprite = pyglet.sprite.Sprite(player_laser_image)

circle_bullet = pyglet.resource.image('res/bullet.png')
center_image(circle_bullet)
circle_bullet_sprite = pyglet.sprite.Sprite(circle_bullet)

oval_bullet = pyglet.resource.image('res/oval_bullet.png')
center_image(oval_bullet)

circle_bullet_white = pyglet.resource.image('res/circle_bullet_white.png')
center_image(circle_bullet_white)

blue_laser = pyglet.resource.image('res/blue_laser.png')
center_image(blue_laser)


# sounds
music = pyglet.media.load('res/THE_WORLD_REVOLVING_Deltarune_OST.wav')
death_sound = pyglet.media.load('res/death_sound.wav')
enemy_attack = pyglet.media.load('res/ATTACK5.wav', streaming = False)
defeat_sound = pyglet.media.load('res/DEFEATED.wav', streaming = False)
damage = pyglet.media.load('res/Damage1.wav', streaming = False)


#fonts
pyglet.font.add_file('res/ethnocentric_rg.ttf')
ethno = pyglet.font.load('ethnocentrig rg')
