import pygame
from image import load_tileset

class Tile(pygame.sprite.Sprite):
    def __init__(self, image, topleft):
        super().__init__()
        self.image = image
        self.rect = image.get_rect(topleft = topleft)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class TileMap(pygame.sprite.Sprite):
    def __init__(self, path, tileset, *groups):
        super().__init__(*groups)
        self.tileset = tileset

        self.map = []
        with open(path, "r") as file:
            for row in file.readlines():
                self.map.append([*map(int, row.split(","))])

        tile_rect = self.tileset[0].get_rect()
        tile_width = tile_rect.w
        tile_height = tile_rect.h
        columns = len(self.map[0])
        rows = len(self.map)
        width = tile_width * columns
        height = tile_height * rows
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        for y in range(rows):
            y0 = y * tile_height
            for x in range(columns):
                tile_index = self.map[y][x]
                if tile_index != -1:
                    x0 = x * tile_width
                    tile_image = self.tileset[tile_index]
                    tile = Tile(tile_image, (x0, y0))
                    tile.draw(self.image)
        self.image.set_colorkey((0, 0, 0))

tileset = load_tileset("data/level/tileset.png", 17, 21, (52, 52))