from settings import screen, FPS
from level import *
from entity import *
from camera import Camera

class SceneManager:
    def __init__(self, main_screen):
        self.scenes = {}
        self.main_screen = main_screen
        self.active_scene_name = ""

    def add_scene(self, scene):
        name = scene.name
        self.scenes[name] = scene

    def change_scene(self, scene_name):
        if self.active_scene_name:
            self.scenes[self.active_scene_name].stop()
        self.active_scene_name = scene_name

    def start(self):
        while self.active_scene_name != None:
            self.scenes[self.active_scene_name].start(self.main_screen)

class Scene:
    def __init__(self, name, SceneManager):
        self.name = name
        self.sm = SceneManager
        self.sm.add_scene(self)
        self.all_sprites = pygame.sprite.Group()
        self.running = False
        self.clock = pygame.time.Clock()

    def scene_logic(self, main_screen):
        ...

    def start(self, main_screen):
        self.running = True
        while self.running:
            self.clock.tick(FPS)
            self.scene_logic(main_screen)

    def stop(self):
        if self.running:
            self.running = False
            self.sm.change_scene(None)

class Game(Scene):
    def __init__(self, SceneManager, name="game"):
        super().__init__(name, SceneManager)
        self.interface = pygame.sprite.Group()

        self.zombies_killed = 0
        self.dxz = 100  # Растояние между зомби
        self.wave_counter = 0  # Номер волны
        self.zombies = pygame.sprite.Group() # Группа зомби
        self.x1, self.x2 = 0, 1280 # Границы камеры

        self.level = pygame.sprite.Group()
        ground = TileMap("data/level/tilemap_ground.csv", tileset, self.all_sprites, self.level)
        walls = TileMap("data/level/tilemap_walls.csv", tileset, self.all_sprites, self.level)
        periphery = TileMap("data/level/tilemap_periphery.csv", tileset, self.all_sprites, self.level)

        self.player = Player(ground.rect.width // 2, self.all_sprites, self.interface)

        self.camera = Camera()

    def spawn_zombies(self):  # Спавн зомби
        n = 0
        xz0 = -((self.wave_counter // 2 + 1) * self.dxz)
        while len(self.zombies.sprites()) != self.wave_counter:
            xz = xz0 + self.dxz * n
            if xz < self.x1 - self.dxz or xz > self.x2 + self.dxz:
                zombie = Zombie(xz, self.all_sprites, self.interface, self.zombies)
                self.zombies.add(zombie)
            n += 1

    def scene_logic(self, main_screen):
        # Спавн зомби
        if len(self.zombies.sprites()) == 0:
            self.wave_counter += 1
            self.spawn_zombies()

        # Проверка столкновений пуль с зомби
        for bullet in self.player.bullets:
            zombies_hit = pygame.sprite.spritecollide(bullet, self.zombies, False, pygame.sprite.collide_mask)
            for zombie in zombies_hit:
                zombie.hp -= self.player.bullet_damage  # Наносим урон зомби
                bullet.kill()
                if zombie.hp <= 0:  # Если здоровье зомби <= 0, он умирает
                    zombie.dead = True
                    self.zombies.remove(zombie)
                    self.zombies_killed += 1
                    zombie.change_animation('dead')

        self.camera.update(self.player)
        bg_image = load_image("data/level/background.png")
        bg_image = pygame.transform.scale(bg_image, screen)
        bg_rect = bg_image.get_rect()
        main_screen.blit(bg_image, bg_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print(f"Количество убитых зомби: {self.zombies_killed}!")
                self.stop()

        self.all_sprites.update()
        self.interface.update()

        # Установка ограничений на камеру по краям карты
        level_sprite_rect = self.level.sprites()[0].rect
        level_x = level_sprite_rect.x
        if level_x + self.camera.dx >= 0:
            self.camera.dx = -level_x

        level_x_min = WIDTH - level_sprite_rect.width
        if level_x_min >= level_x + self.camera.dx:
            self.camera.dx = level_x_min - level_x

        # Обновление камеры
        for sprite in self.all_sprites:
            self.camera.apply(sprite)

        self.level.draw(main_screen)
        self.interface.draw(main_screen)
        self.all_sprites.draw(main_screen)
        pygame.display.flip()