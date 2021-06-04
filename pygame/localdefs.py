import os.path
import os
import pygame


def imgLoad(img):
    file = os.path.join(img)
    image = pygame.image.load(file)
    image.convert_alpha()
    return image
