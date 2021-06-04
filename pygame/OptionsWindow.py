import pygame
from pygame.locals import *
import localdefs
import os
import sys

clock = pygame.time.Clock()
pygame.init()
f = open('resolution.txt', 'r')
pygame.init()
size = width, height = [int(a) for a in f.read().split('x')]

screen = pygame.display.set_mode(size)


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


def options_window(clock, size):
    global flag
    flag = True
    width, height = size
    pygame.mouse.set_visible(True)
    imgs = dict()
    rects = dict()
    screen = pygame.display.set_mode((width, height))
    bg = pygame.Surface((width, height))
    imgs[0] = localdefs.imgLoad('optionsimages/Options.png')
    rects[0] = imgs[0].get_rect(centerx=width / 2, centery=height / 5)
    for num, i in enumerate(["Res1920", "Res1280", 'exit']):
        imgs[i] = localdefs.imgLoad(os.path.join("optionsimages", i + ".png"))
        rects[i] = imgs[i].get_rect(centerx=width / 2, centery=(num + 1 + 1) * height / 6)
    BackGround = Background('menuimages/pixil.png', [0, 0])
    bg.fill([255, 255, 255])
    bg.blit(pygame.transform.scale(BackGround.image, (width, height)), BackGround.rect)
    clock.tick(40)
    screen.blit(bg, (0, 0))
    run = True
    while run:
        for key in imgs.keys():
            screen.blit(imgs[key], rects[key])
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                if rects["Res1280"].collidepoint(event.dict['pos']):
                    width1, height1 = 1280, 720
                    chages(size, width1, height1)
                    run = False
                elif rects["Res1920"].collidepoint(event.dict['pos']):
                    width1, height1 = 1920, 1080
                    chages(size, width1, height1)
                    run = False
                elif rects["exit"].collidepoint(event.dict['pos']):
                    flag = False
                    running()
                    run = False
        pygame.display.flip()


def chages(size, width1, height1):
    width, height = size
    pygame.font.init()
    sc = pygame.display.set_mode((width, height))
    sc.fill((0, 0, 0))
    f1 = pygame.font.Font(None, width // 25)
    text1 = f1.render("Вы хотите изменить разрешение?", True,
                      (255, 255, 255))
    f2 = pygame.font.SysFont('serif', width // 25)
    text2 = f2.render("Если да, нажмите F, чтобы перезапустить приложение", False,
                      (255, 255, 255))
    sc.blit(text1, (10, 50))
    sc.blit(text2, (10, height - width // 25 * 3))
    pygame.display.update()
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    run = False
                    print(width1, height1)
                    f = open('resolution.txt', 'w')
                    f.write(f'{width1}x{height1}')
                    f.close()
                    os.startfile("GameWindow.pyw")


def running():
    return flag