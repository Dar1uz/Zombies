import pygame
from image import load_image, load_spritesheet
from settings import FPS, GRAVITY, WIDTH, HEIGHT
from math import atan2, cos, sin, degrees
from random import randint

class Animation:
    def __init__(self, name: str, is_cyclical: bool, is_forced: bool, is_interrupted: bool, path: str, count: int,
                 size: tuple, colorkey = None):
        self.name = name
        self.is_cyclical = is_cyclical
        self.is_forced = is_forced
        self.is_interrupted = is_interrupted

        self.frames = load_spritesheet(path, count, size, colorkey)

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, animations: list, fps: int, *groups):
        super().__init__(*groups)

        # Поля, отвечающие за изображение
        self.image = None
        self.flip_x = False
        self.rect = None
        self.mask = None

        # Поля, отвечающие за анимацию
        self.active_animation_name = None
        self.FPS = fps
        self.frame = 0
        self.counter = 0

        # Загрузка анимаций
        self.animations = {}
        for animation in animations:
            self.add_animation(animation)
            if not self.active_animation_name:
                self.change_animation(animation.name)
                self.next_frame()

    def add_animation(self, animation):
        animation_name = animation.name
        self.animations[animation_name] = animation

    def set_sprite(self, image):
        self.image = pygame.transform.flip(image, self.flip_x, False)
        if self.rect:
            self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        else:
            self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def next_frame(self):
        name = self.active_animation_name
        if not name:
            return False

        animation = self.animations[name]

        if not self.image:
            image = animation.frames[0]
            self.set_sprite(image)
            return True

        if self.counter == FPS // self.FPS:
            frames_count = len(animation.frames)
            self.frame = (self.frame + 1) % frames_count
            image = animation.frames[self.frame]
            self.set_sprite(image)
            self.counter = 0
            if self.frame == frames_count - 1:
                if animation.is_cyclical:
                    return True
                self.active_animation_name = None
                return False

        else:
            image = animation.frames[self.frame]
            self.set_sprite(image)

        self.counter += 1
        return True

    def change_animation(self, animation_name):
        if not self.active_animation_name:
            self.active_animation_name = animation_name
            return True

        else:
            if animation_name != self.active_animation_name:
                self.active_animation_name = animation_name
                self.frame = 0
                self.counter = 0
                return True

    def update(self): self.next_frame()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos):
        super().__init__()
        self.bullet_speed = 30

        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        angle = atan2(dy, dx)
        self.vx = cos(angle) * self.bullet_speed
        self.vy = sin(angle) * self.bullet_speed

        image = load_image("data/extras/bullet.png")
        image = pygame.transform.scale(image, (30, 30))
        self.image = pygame.transform.rotate(image, -degrees(angle))
        self.rect = self.image.get_rect(center=start_pos)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.right < 0 or self.rect.left > WIDTH or self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

class Player(AnimatedSprite):
    def __init__(self, x, all_sprites, interface):
        # Группы спрайтов
        self.all_sprites = all_sprites
        self.bullets = pygame.sprite.Group()

        # Характеристики персонажа
        self.hp = 100
        self.dead = False

        self.vx = 5
        self.vy = 0
        self.jump_height = 15
        self.on_ground = True

        self.fire_timer = 0
        self.reload_time = 60
        self.reload_timer = 0
        self.magazine_size = 30
        self.bullets_count = self.magazine_size
        self.fire_rate = 20
        self.reloading = True
        self.bullet_damage = 35

        # Найстройки анимации
        size = (250, 250)
        idle = Animation("idle", True, False, True,
                         'data/solider/Idle.png', 9, size)
        run = Animation("run", True, False, True,
                        'data/solider/Run.png', 8, size)
        shot = Animation("shot", False, True, True,
                         'data/solider/Shot.png', 4, size)
        dead = Animation("dead", False, True, True,
                         'data/solider/Dead.png', 4, size)
        animations = [idle, run, shot, dead]

        # Загрузка анимации
        super().__init__(animations, 10, all_sprites, interface)
        self.rect.x = x
        self.rect.y = HEIGHT - 92 - self.rect.height

    def shoot(self, mouse_pos):
        self.change_animation("shot")
        if self.bullets_count > 0 and not self.reloading and self.fire_timer == 0:
            bullet = Bullet((self.rect.x + self.rect.width / 2, self.rect.y + self.rect.height / 1.48), mouse_pos)
            self.all_sprites.add(bullet)
            self.bullets.add(bullet)
            self.bullets_count -= 1
            self.fire_timer = self.fire_rate  # Устанавливаем задержку
            if self.bullets_count == 0:
                self.reloading = True

    def update(self):
        if not self.dead:
            # Получение действий игрока
            # Разворот и стрельба
            mouse_pos = pygame.mouse.get_pos()

            player_x = self.rect.x + self.rect.width / 2
            if mouse_pos[0] > player_x:
                self.flip_x = False
            else:
                self.flip_x = True

            mouse_pressed = pygame.mouse.get_pressed()
            if mouse_pressed[0]:
                self.shoot(mouse_pos)

            else:
                # Бег
                keys = pygame.key.get_pressed()
                if keys[pygame.K_a]:
                    self.rect.x -= self.vx
                    self.change_animation("run")
                if keys[pygame.K_d]:
                    self.rect.x += self.vx
                    self.change_animation("run")

                if not(keys[pygame.K_a] or keys[pygame.K_d]):
                    self.change_animation("idle")

                # Прыжок
                if keys[pygame.K_SPACE] and self.on_ground:
                    self.vy = -self.jump_height
                    self.on_ground = False

            # Гравитация
            self.vy += GRAVITY
            self.rect.y += self.vy

            # Ограничение на падение
            if self.rect.y + self.rect.height >= HEIGHT - 92:
                self.rect.y = HEIGHT - 92 - self.rect.height
                self.on_ground = True
                self.vy = 0

            # Перезарядка
            if self.reloading:
                self.reload_timer += 1
                if self.reload_timer >= self.reload_time:
                    self.bullets_count = self.magazine_size
                    self.reloading = False
                    self.reload_timer = 0

            # Задержка стрельбы
            if self.fire_timer > 0:
                self.fire_timer -= 1

            if self.hp <= 0:
                self.dead = True
                self.change_animation("dead")
        super().update()

# Класс зомби
class Zombie(AnimatedSprite):
    def __init__(self, x, all_sprites, interface, zombies):
        # Группы спрайтов
        self.all_sprites = all_sprites
        self.player = interface.sprites()[0]

        # Характеристики персонажа
        self.hp = 100
        self.vx = 4
        self.damage = 10
        self.dead = False

        self.attack = False

        # Найстройки анимации
        size = (250, 250)
        frames = {
            "walk": [10, 10, 10, 12],
            "attack": [5, 5, 4, 10],
            "dead": [5, 5, 5, 5],
            "idle": [6, 6, 6, 7]
        }
        i = randint(1, 4)
        walk = Animation("walk", True, False, True,
                        f'data/zombies/{i}/Walk.png', frames["walk"][i - 1], size)
        attack = Animation("attack", False, False, True,
                         f'data/zombies/{i}/Attack.png', frames["attack"][i - 1], size)
        dead = Animation("dead", False, False, True,
                           f'data/zombies/{i}/Dead.png', frames["dead"][i - 1], size)
        idle = Animation("idle", False, False, True,
                         f'data/zombies/{i}/Idle.png', frames["idle"][i - 1], size)
        animations = [walk, attack, dead, idle]

        # Загрузка анимации
        super().__init__(animations, 10, all_sprites, zombies)
        self.rect.x = x
        self.rect.y = HEIGHT - 92 - self.rect.height

    def update(self):
        if not self.player.dead:
            if not self.dead:
                if not self.attack:
                    if self.rect.x < self.player.rect.x:
                        self.rect.x += self.vx
                        self.flip_x = False
                    else:
                        self.rect.x -= self.vx
                        self.flip_x = True
                    self.change_animation("walk")

                    # Урон игроку при касании
                    if pygame.sprite.collide_mask(self, self.player):
                        if not self.attack:
                            self.attack = True
                            self.player.hp -= self.damage
                            self.change_animation("attack")

        if not self.next_frame():
            self.attack = False
            if not self.dead:
                self.change_animation("idle")
            else:
                self.kill()