import pygame
import localdefs
import os

f = open('resolution.txt', 'r')
pygame.init()
size = width, height = [int(a) for a in f.read().split('x')]

pygame.init()

fps = 144

fps_clock = pygame.time.Clock()
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Tower Defense Bullet Hell')
screen.fill((255, 255, 255))


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


def level_window():
    global level, flag
    level = "level_2"
    run = True
    flag = True
    imgs = {}
    rects = {}
    bg = pygame.Surface(size)
    while run:
        pygame.mouse.set_visible(True)
        f = open('resolution.txt', 'r')
        pygame.init()
        size1 = width1, height1 = [int(a) for a in f.read().split('x')]
        screen = pygame.display.set_mode(size)
        BackGround = Background('menuimages/pixil.png', [0, 0])
        bg.fill([255, 255, 255])
        bg.blit(pygame.transform.scale(BackGround.image, (width1, height1)), BackGround.rect)
        screen.blit(bg, (0, 0))
        for num, i in enumerate(["lvl_1", "lvl_2", "lvl_3", "lvl_4", "lvl_5", "exit"]):
            imgs[i] = localdefs.imgLoad(os.path.join("levels", i + ".png"))
            rects[i] = imgs[i].get_rect(centerx=size1[0] / 2, centery=(num + 1) * size1[1] / 7)
        for key in imgs.keys():
            screen.blit(imgs[key], rects[key])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONUP:
                if rects["lvl_1"].collidepoint(event.dict['pos']):
                    level = "level1"
                    run = False
                    Game_level()
                elif rects["lvl_2"].collidepoint(event.dict['pos']):
                    level = "level2"
                    run = False
                    Game_level()
                elif rects["lvl_3"].collidepoint(event.dict['pos']):
                    level = "level3"
                    run = False
                    Game_level()
                elif rects["lvl_4"].collidepoint(event.dict['pos']):
                    level = "level4"
                    run = False
                    Game_level()
                elif rects["lvl_5"].collidepoint(event.dict['pos']):
                    level = "level5"
                    run = False
                    Game_level()
                elif rects["exit"].collidepoint(event.dict['pos']):
                    flag = False
                    running()
                    run = False
        pygame.display.flip()
        # Обновим экран.
        fps_clock.tick(fps)
        # Тик.


def Game_level():
    return level


def running():
    return flag