# Подключение основной библиотеки настроек игры и ее запуск
import pygame
from settings import screen

pygame.init()
# pygame.mouse.set_visible(False)
main_screen = pygame.display.set_mode(screen, pygame.FULLSCREEN)


# Подключение игровых сцен и менеджера
from scenes import SceneManager, Game

sm = SceneManager(main_screen)
game = Game(sm)

# Выбор и запуск сцены
sm.change_scene("game")
sm.start()
pygame.quit()