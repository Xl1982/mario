import arcade
import arcade.gl
import arcade.gui
from arcade.gui import UIManager
from arcade.gui.widgets import UIAnchorWidget, UIBoxLayout, UILabel
import math
import os

SCREEN_TITLE = "РћРєРЅР°"

SPRITE_IMAGE_SIZE = 128
TILE_SCALING = 1
SPRITE_SCALING_PLAYER = 1.5
SPRITE_SCALING_TILES = 1
CHARACTER_SCALING = 1.5
SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_PLAYER)

SCREEN_GRID_WIDTH = 25
SCREEN_GRID_HEIGHT = 15

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

GRAVITY = 1500

DEFAULT_DAMPING = 1.0
PLAYER_DAMPING = 0.4

PLAYER_FRICTION = 1.0
WALL_FRICTION = 0.3
DYNAMIC_ITEM_FRICTION = 0.6

PLAYER_MASS = 2.0
PLAYER_MOVE_FORCE_IN_AIR = 500

PLAYER_MAX_HORIZONTAL_SPEED = 300
PLAYER_MAX_VERTICAL_SPEED = 1600
SAW_SCALING = 0.3
PLAYER_MOVE_FORCE_ON_GROUND = 999
DEAD_ZONE = 0.1
PLAYER_JUMP_IMPULSE = 1500
PLAYER_JUMP_SPEED = 30
COIN_SCALE = 0.3
RIGHT_FACING = 0
LEFT_FACING = 1
EXIT_SCALING = 0.3
DISTANCE_TO_CHANGE_TEXTURE = 20
BIG_COIN_SCALE = 0.8
VIEWPORT_MARGIN = 200
i = 500
ENEMY_SCALING = 1.5
ENEMY_MASS = 2.0
ENEMY_MAX_HORIZONTAL_SPEED = 300
ENEMY_MAX_VERTICAL_SPEED = 1600
ENEMY_FRICTION = 1


def _gen_initial_data(initial_x, initial_y):
    yield initial_x
    yield initial_y


class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()


def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]


class PlayerSprite(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.scale = SPRITE_SCALING_PLAYER

        main_path = "mario/mario"

        self.idle_texture_pair = arcade.load_texture_pair(f"{main_path}_idle.png")
        self.jump_texture_pair = arcade.load_texture_pair(f"{main_path}_jump.png")
        self.slide_texture_pair = arcade.load_texture_pair(f"{main_path}_slide.png")
        self.crouch = arcade.load_texture_pair(f"mario/mario_crouch.png")
        self.walk_textures = []
        for i in range(3):
            texture = arcade.load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        self.texture = self.idle_texture_pair[0]

        self.hit_box = self.texture.hit_box_points
        self.character_face_direction = RIGHT_FACING
        self.cur_texture = 0
        self.x_odometer = 0

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        if dx < -DEAD_ZONE and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
            self.texture = self.slide_texture_pair[self.character_face_direction]
        elif dx > DEAD_ZONE and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
            self.texture = self.slide_texture_pair[self.character_face_direction]

        if abs(self.x_odometer) > DISTANCE_TO_CHANGE_TEXTURE:

            self.x_odometer = 0

            self.cur_texture += 1
            if self.cur_texture > 2:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]

        is_on_ground = physics_engine.is_on_ground(self)

        self.x_odometer += dx

        if not is_on_ground:
            if dy > DEAD_ZONE:
                self.texture = self.jump_texture_pair[self.character_face_direction]
                return
            elif dy < -DEAD_ZONE:
                self.texture = self.jump_texture_pair[self.character_face_direction]
                return

        if abs(dx) <= DEAD_ZONE:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        if abs(self.x_odometer) > DISTANCE_TO_CHANGE_TEXTURE:

            self.x_odometer = 0

            self.cur_texture += 1
            if self.cur_texture > 2:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]
    def squat(self):
            self.x_odometer = 0
            self.texture = self.crouch[self.character_face_direction]


class GameOver(arcade.View):
    def __init__(self):
        super(GameOver, self).__init__()
        self.background = None
        self.lose_sound = arcade.load_sound('sounds/smw_game_over.wav')
        arcade.play_sound(self.lose_sound, volume=1.2, looping=False)


    def setup(self):
        self.background = arcade.load_texture('background/maxresdefault.jpg')

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            game_view = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
            game_view.setup()
            self.window.show_view(game_view)
            pass

    def on_draw(self):
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)
        arcade.draw_text('Press ENTER to try again', start_x=300, start_y=100, color=(255, 255, 255), width=200)


class MenuView(arcade.View):
    def __init__(self):
        super(MenuView, self).__init__()
        self.manager = UIManager()
        self.manager.enable()
        arcade.set_background_color(arcade.color.WHITE)
        self.v_box = arcade.gui.UIBoxLayout()
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )
        start_button = arcade.gui.UIFlatButton(text="Start Game", width=200, )
        self.v_box.add(start_button.with_space_around(bottom=20))

        settings = arcade.gui.UIFlatButton(text="Settings", width=200)
        self.v_box.add(settings.with_space_around(bottom=50))

        quit_button = QuitButton(text="Quit", width=200)
        self.v_box.add(quit_button)
        start_button.on_click = self.on_click_start
        settings.on_click = self.on_click_open

    def on_click_open(self, event):
        print('open')
        message_box = arcade.gui.UIMessageBox(

            width=300,

            height=200,

            message_text=(

                "Здесь были настройки"

            ),

            callback=self.on_message_box_close,

            buttons=["а куда ", "Ладно"]

        )

        self.manager.add(message_box)

    def on_click_start(self, event):
        game_view = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        game_view.setup()
        self.window.show_view(game_view)
        pass

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_message_box_close(self, button_text):
        print(f"User pressed {button_text}.")

        pass


class UINumberLabel(UILabel):
    _value: float = 0

    def __init__(self, value=0, format="{value:.0f}", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format = format
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.text = self.format.format(value=value)
        self.fit_content()


class GameWindow(arcade.View):
    def __init__(self, width, height, title, ):
        super().__init__()
        self.crouch = None
        self.block = None
        self.question = None
        self.enemy_layer = None
        self.goomba_list = None
        self.camera = None
        self.game_over = None
        self.view_left = 0
        self.view_bottom = 0
        self.coin = None
        self.background_list = None
        self.mushroom = None
        self.music1 = None
        self.player_sprite = None
        self.player_list = None
        self.wall_list = None
        self.left_pressed = False
        self.right_pressed = False
        self.down_pressed = False
        self.physics_engine = None
        self.jump_sound = None
        self.jump_sound_player = None
        self.lose_sound = None
        self.lose_sound_player = None
        self.music = None
        self.sound = None
        self.goomba = None
        self.manager = UIManager()
        self.manager.enable()
        self.lives = UINumberLabel(3)
        self.score = UINumberLabel(0)
        self.columns = UIBoxLayout(
            vertical=False,
            children=[
                UIBoxLayout(vertical=True, children=[
                    UILabel(text="lives:", width=50, ),
                    UILabel(text="coins:", width=50),

                ]),

                UIBoxLayout(vertical=True, children=[
                    self.lives,
                    self.score
                ]),
            ])

        self.manager.add(UIAnchorWidget(
            align_x=10,
            anchor_x="left",
            align_y=-10,
            anchor_y="top",
            child=self.columns
        ))

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
                self.camera.viewport_height / 2
        )

        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def setup(self):
        self.background_list = arcade.SpriteList()
        background = arcade.Sprite('background/6208.png')
        background.center_x = 100 + i
        background.center_y = -230
        self.background_list.append(background)
        self.camera = arcade.Camera(800, 600)
        self.view_left = 0
        self.view_bottom = 0
        self.player_list = arcade.SpriteList()
        self.question_list = arcade.SpriteList()
        map_name = "map/5.json"
        tile_map = arcade.load_tilemap(map_name, SPRITE_SCALING_TILES)
        print(tile_map.sprite_lists)
        self.mushroom = tile_map.sprite_lists['mushromblock']
        self.block = tile_map.sprite_lists['brick']
        self.question = tile_map.sprite_lists['questionblock']
        self.wall_list = tile_map.sprite_lists['Слой тайлов 1']
        self.crouch = arcade.load_texture_pair(f"mario/mario_crouch.png")
        self.player_sprite = PlayerSprite()
        self.player_sprite.center_x = 100
        self.player_sprite.center_y = 100
        self.player_list.append(self.player_sprite)
        self.coin = tile_map.sprite_lists['coins']

        damping = DEFAULT_DAMPING
        gravity = (0, -GRAVITY)
        self.physics_engine = arcade.PymunkPhysicsEngine(damping=damping,
                                                         gravity=gravity)
        self.physics_engine.add_sprite(self.player_sprite,
                                       friction=PLAYER_FRICTION,
                                       mass=PLAYER_MASS,
                                       moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="player",
                                       max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
                                       max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED)
        self.physics_engine.add_sprite_list(self.wall_list,
                                            friction=WALL_FRICTION,
                                            collision_type="wall",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)
        self.physics_engine.add_sprite_list(self.block,
                                            friction=WALL_FRICTION,
                                            collision_type="wall",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)
        self.physics_engine.add_sprite_list(self.question,
                                            friction=WALL_FRICTION,
                                            collision_type="wall",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC
                                            )

        self.jump_sound = arcade.load_sound("sounds/smw_jump.wav")
        self.power_up_sound = arcade.load_sound("sounds/smw_power-up.wav")
        self.sound = arcade.load_sound('Super Mario Bros. - Overworld (Main Theme) [Remix] (256  kbps).mp3')
        self.music1 = arcade.play_sound(self.sound, volume=0.2, looping=True)
        pass

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.UP:
            if self.physics_engine.is_on_ground(self.player_sprite):
                impulse = (0, PLAYER_JUMP_IMPULSE)
                self.physics_engine.apply_impulse(self.player_sprite, impulse)
                self.jump_sound_player = arcade.play_sound(self.jump_sound, volume=1.5, looping=False)
        elif key == arcade.key.DOWN:
            print('Присел')
            self.down_pressed = True
            self.player_sprite.squat()
        elif key == arcade.key.ESCAPE:
            arcade.stop_sound(self.music1)
            game_view = MenuView()
            self.window.show_view(game_view)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False


    def on_update(self, delta_time):
        is_on_ground = self.physics_engine.is_on_ground(self.player_sprite)
        if self.left_pressed and not self.right_pressed:
            if is_on_ground:
                force = (-PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (-PLAYER_MOVE_FORCE_IN_AIR, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.right_pressed and not self.left_pressed:
            if is_on_ground:
                force = (PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (PLAYER_MOVE_FORCE_IN_AIR, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            self.physics_engine.set_friction(self.player_sprite, 0)
        else:
            self.physics_engine.set_friction(self.player_sprite, 1.0)
            hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.question)
            if hit_list:
                arcade.exit()
            coin = arcade.check_for_collision_with_list(self.player_sprite, self.coin)
            for i in self.coin:
                if coin:
                    self.score.value += 1
                    i.kill()
            mushroom = arcade.check_for_collision_with_list(self.player_sprite, self.mushroom)
            for i in mushroom:
                if mushroom:
                    arcade.play_sound(self.power_up_sound, volume=1.5, looping=False)
                    i.kill()


        self.physics_engine.step()
        if self.player_sprite.center_y < 0:
            self.game_over = True
        if self.game_over:
            self.lives.value -= 1
            if self.score.value > 0:
               self.score.value -= 5
            else:
                self.score.value += 0
            arcade.stop_sound(self.music1)
            self.setup()
            self.update(delta_time)
            self.game_over = False
        if self.lives.value < 1:
            game_view = GameOver()
            arcade.stop_sound(self.music1)
            game_view.setup()
            self.window.show_view(game_view)

        self.center_camera_to_player()

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.background_list.draw()
        self.wall_list.draw()
        self.player_list.draw()
        self.block.draw()
        self.coin.draw()
        self.question.draw()
        self.manager.draw()
        self.mushroom.draw()



if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = MenuView()
    window.show_view(start_view)
    arcade.run()
