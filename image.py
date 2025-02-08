import pygame

def load_image(path, colorkey=None):
    image = pygame.image.load(path)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

def load_tileset(path, columns, rows, size, colorkey=None):
    image = load_image(path, colorkey)
    rect = image.get_rect()
    width = rect.w / columns
    height = rect.h / rows

    tileset = []
    for y in range(rows):
        y0 = y * height
        for x in range(columns):
            x0 = x * width
            tile_image = image.subsurface((x0, y0, width, height))
            tile_image = pygame.transform.scale(tile_image, size)
            tileset.append(tile_image)
    return tileset

def load_spritesheet(path, count, size, colorkey=None):
    return load_tileset(path, count, 1, size, colorkey)