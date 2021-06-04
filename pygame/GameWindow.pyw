# -*- coding: utf-8 -*-
import pygame
import os
import random
import math

import res_win
import SelectMap
import OptionsWindow

winn = False
overr = False
clock = pygame.time.Clock()
pygame.init()
f = open('resolution.txt', 'r')
pygame.init()
size = width, height = [int(a) for a in f.read().split('x')]
fps = 144
fps_clock = pygame.time.Clock()
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Tower Defense Bullet Hell')
enemy_bullets = pygame.sprite.Group()
# Группа спрайтов вражеских пуль.
cursor_group = pygame.sprite.Group()
# Группа для курсора.
enemy_group = pygame.sprite.Group()
# Группа врагов.
friendly_bullets = pygame.sprite.Group()
# Группа дружелюбных пуль.
towers_group = pygame.sprite.Group()
# Группа башен.
base_group = pygame.sprite.Group()
pygame.mouse.set_visible(False)


# Скрываем основной курсор ОС, у нас он круче.


def crop(image, color_key=None):
    # Пришлось вынести кусок load_image отдельно, чтобы удалять фон у картинок с измененным размером.
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def load_image(name, color_key=None):
    # Стандартная функция подгрузки картинок.
    fullname = os.path.join('Data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    return crop(image, color_key)


class Board:
    # Стандартный класс-основа клеточного поля.

    def __init__(self, cols, rows, siz, x_indent, y_indent):
        self.columns = cols
        self.rows = rows
        self.cells_data = [[0] * rows for _ in range(cols)]
        self.cell_size = siz
        self.indent = [x_indent, y_indent]
        return

    def render(self, surface):
        surface.fill((0, 0, 0))
        for i in range(self.columns):
            for j in range(self.rows):
                if self.cells_data[i][j] == 1:
                    pygame.draw.rect(surface, (0, 255, 0), (i * self.cell_size + self.indent[
                        0], j * self.cell_size + self.indent[1], self.cell_size, self.cell_size))
                pygame.draw.rect(surface, (255, 255, 255), (i * self.cell_size + self.indent[
                    0], j * self.cell_size + self.indent[1], self.cell_size, self.cell_size), 1)
        return

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell)
        return

    def get_cell(self, mouse_pos):
        cell = ((mouse_pos[0] - self.indent[0]) // self.cell_size, (mouse_pos[1] - self.indent[1]) // self.cell_size)
        if cell[0] >= self.columns or cell[0] < 0 or cell[1] >= self.rows or cell[1] < 0:
            return None
        return cell

    def on_click(self, cell):
        return


def search_for_road(pos, pr, board):
    # DFS, ищущий путь.
    directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]
    for direction in directions:
        new_pos = [pos[0] + direction[0], pos[1] + direction[1]]
        if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] >= 28 or new_pos[1] >= 12 or new_pos == pr:
            continue
        if board.cells_data[new_pos[0]][new_pos[1]] == 1:
            road.append([board.indent[0] + pos[0] * board.cell_size, board.indent[1] + pos[1] * board.cell_size])
            search_for_road(new_pos, pos, board)
            break
    return


class Field(Board):
    # Класс главного поля.

    def __init__(self, level_name):
        super().__init__(28, 12, int(width // 30), 64, 64)
        self.selected = [-1, -1]
        # Хранит выделенную клетку.
        level_map_file = open('levels\\' + level_name + '_map.txt')
        level_map_data = level_map_file.read().split('\n')
        level_map_file.close()
        # Считываем карту с .txt-файла.
        for i in range(len(level_map_data)):
            for j in range(len(level_map_data[i])):
                if level_map_data[i][j] == '#':
                    self.cells_data[j][i] = 1
                elif level_map_data[i][j] == '%':
                    self.cells_data[j][i] = 3
                # Записываем эи данные.
        # Теперь найдем путь, по которому пройдут монстры.
        for j in range(28):
            if self.cells_data[0][j] == 1:
                search_for_road([0, j], [-1, -1], self)
                break
        # Теперь в road хранится путь.
        return

    def render(self, surface):
        # Обычный render.
        for i in range(self.columns):
            for j in range(self.rows):
                if self.cells_data[i][j] != 1:
                    pygame.draw.rect(surface, (255, 255, 255), (i * self.cell_size + self.indent[
                        0], j * self.cell_size + self.indent[1], self.cell_size, self.cell_size), 1)
                    # Обводка.
                if self.cells_data[i][j] == 3:
                    pygame.draw.rect(surface, (32, 32, 32), (i * self.cell_size + self.indent[
                        0], j * self.cell_size + self.indent[1], self.cell_size, self.cell_size))
                    # Выделение запрещенных ячеек.
                    pygame.draw.rect(surface, (128, 128, 128), (i * self.cell_size + self.indent[
                        0], j * self.cell_size + self.indent[1], self.cell_size, self.cell_size), 1)
                    # Обводка для запрещенных ячеек.
                if i == self.selected[0] and self.selected[1] == j:
                    pygame.draw.rect(surface, (255, 255, 255), (i * self.cell_size + self.indent[
                        0], j * self.cell_size + self.indent[1], self.cell_size, self.cell_size), 8)
                    # Обводка выделенной клетки.
        return

    def on_click(self, cell):
        if self.cells_data[cell[0]][cell[1]] == 0 and cursor.selected_tower != 0 and cursor.coins >= shop.products[
            shop.selected][1]:
            self.cells_data[cell[0]][cell[1]] = cursor.selected_tower([cell[0] * self.cell_size + 64, cell[
                1] * self.cell_size + 64], towers_group)
            towers_list.append(self.cells_data[cell[0]][cell[1]])
            cursor.coins -= shop.products[shop.selected][1]
            self.selected = cell

            sound = pygame.mixer.Sound('Data/installation.mp3')
            sound.set_volume(0.2)
            pygame.mixer.Channel(0).play(sound)
            # Ставим башню.
        elif self.cells_data[cell[0]][cell[1]] != 1 and self.cells_data[cell[0]][cell[1]] != 0 and self.cells_data[
            cell[0]][cell[1]] != 3:
            if self.selected == cell:
                # Убираем выделение.
                self.selected = [-1, -1]
            else:
                # Выделяем башню.
                self.selected = cell
        return


class Bullet(pygame.sprite.Sprite):
    # Основной класс простейшей пули.
    image = pygame.transform.scale(load_image('Simple_bullet.png', -1), (int(width // 60), int(height // 33.75)))
    image = crop(image, -1)

    def __init__(self, current_position, speed, direction, radius, damage, max_age, *group):
        super().__init__(*group)
        # Инициация спрайта.
        self.age = 0
        self.max_age = max_age
        # "Возраст" пули.
        self.image = pygame.transform.scale(Bullet.image, (radius + radius, radius + radius))
        # Изменение картинки для получения нужного радиуса.
        self.rect = self.image.get_rect()
        self.direction = direction
        # Направление движения пули.
        self.speed = speed * height / 1080 / fps
        # Перевод скорости в секунду в скорость в тик.
        self.current_position = current_position
        # Позиция пули.
        self.rect.topleft = (int(self.current_position[0]), int(self.current_position[1]))
        self.coefficient = 1 / ((self.direction[0] ** 2 + self.direction[1] ** 2) ** 0.5)
        # Это нужно, чтобы от self.direction не зависила скорость.
        self.radius = radius
        # Размер пули.
        self.colour = (255, 255, 255)
        # Цвет пули.
        self.mask = pygame.mask.from_surface(self.image)
        # Маска пули для проверки столкновений.
        self.damage = damage
        # Урон, наносимый пулей.
        return

    def update(self):
        self.age += 1
        if self.age >= self.max_age:
            self.current_position = [-1000, -1000]
            self.rect.topleft = (int(self.current_position[0]), int(self.current_position[1]))
            return True
        current_dist = self.speed * self.coefficient
        self.current_position[0] += self.direction[0] * current_dist
        self.current_position[1] += self.direction[1] * current_dist
        self.rect.topleft = (int(self.current_position[0]), int(self.current_position[1]))
        # Обновляем положение пули.
        # Вернем True, если пуля вышла за экран, и нам она больше не интересна.
        return (self.current_position[0] > size[0] or self.current_position[
            0] + self.radius + self.radius < 0 or self.current_position[1] > size[1] or self.current_position[
                    1] + self.radius + self.radius < 0)

    def set_pos(self, position=(-1000, -1000)):
        # Телепортируем пулю. Эта штука введена, чтобы убирать ее куда подальше, когда она нам уже не нужна.
        self.current_position = position
        self.rect.topleft = (int(self.current_position[0]), int(self.current_position[1]))
        return


class PlusBullet(Bullet):
    # Пуля для башни-плюса.
    image = pygame.transform.scale(load_image('PlusBullet.png', -1), (int(width / 60), int(height * 16 / 525)))
    image = crop(image, -1)

    def __init__(self, current_position, speed, direction, radius, damage, max_age, *group):
        super().__init__(current_position, speed, direction, radius, damage, max_age, group)
        self.image = crop(pygame.transform.scale(PlusBullet.image, (radius + radius, radius + radius)), -1)
        return


class HomingBullet(Bullet):
    # Пуля с самонаведением.
    image = pygame.transform.scale(load_image('HomingBullet.png', -1), (int(width // 60), int(height // 33.75)))
    image = crop(image, -1)

    def __init__(self, current_position, target, *group):
        self.target = target
        # Up-to-date положение цели.
        direction = [self.target.curr_position[0] - current_position[0], self.target.curr_position[
            0] - current_position[0]]
        # Наводимся на цель.
        super().__init__(current_position, 512, direction, 64, 512, 1e9 + 7, group)
        self.image = crop(pygame.transform.scale(HomingBullet.image, (
            self.radius + self.radius, self.radius + self.radius)), -1)
        self.mask = pygame.mask.from_surface(self.image)
        # Маска для столкновений.
        return

    def update(self):
        if self.target.curr_position[0] != -1000:
            self.direction = [self.target.curr_position[0] - self.current_position[0] - 32, self.target.curr_position[
                1] - self.current_position[1] - 32]
            self.coefficient = 1 / ((self.direction[0] ** 2 + self.direction[1] ** 2) ** 0.5)
            # Это нужно, чтобы от self.direction не зависила скорость.
        super().update()
        return


class Cursor(pygame.sprite.Sprite):
    # Стандартный класс курсора.
    standard_image = pygame.transform.scale(load_image('Standard_cursor.png', -1),
                                            (int(width // 60), int(height // 33.75)))
    invincible_standard_image = pygame.transform.scale(load_image('Standard_cursor_invincible.png', -1),
                                                       (int(width // 60), int(height // 33.75)))
    standard_image = crop(standard_image, -1)
    invincible_standard_image = crop(invincible_standard_image, -1)

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Cursor.standard_image
        # Устанавливаем спрайт.
        self.rect = self.image.get_rect()
        self.curr_position = [0, 0]
        self.rect.topleft = (self.curr_position[0] - 16, self.curr_position[1] - 16)
        self.mask = pygame.mask.from_surface(self.image)
        # Настраиваем маску для столкновений.
        self.hp = 1000
        # ХП курсора.
        self.invincible = 0
        # Время неуязвимости курсора (в тиках).
        self.selected_tower = 0
        # Башня, которую сейчас выбрал курсор.
        self.coins = 200
        # Деньги курсора.
        return

    def update(self, position):
        self.curr_position = position
        k = int(width // 60) // 2
        self.rect.topleft = (self.curr_position[0] - k, self.curr_position[1] - k)
        # Обновляем позицию курсора.
        return

    def attack(self, bullet):
        # Бьем курсор!
        if self.invincible:
            # А, нет, он неуязвим. Упс.
            return
        self.hp = max(self.hp - bullet.damage, 0)
        sound = pygame.mixer.Sound('Data/hit.wav')
        sound.set_volume(0.3)
        pygame.mixer.Channel(1).play(sound)
        # Бьем курсор!
        if self.hp == 0:
            # Вызов экрана game-over.
            game_over()
        self.invincible = fps
        # Даем курсору временную неуязвимость.
        self.image = Cursor.invincible_standard_image
        # Отображаем курсор иначе, чтобы показать его неуязвимость. Обновлять маску нет нужды, его все равно нельзя
        # ударить.
        return

    def update_invincibility(self):
        # Обновляем время неуязвимости.
        self.invincible -= 1
        if self.invincible == 0:
            self.image = Cursor.standard_image
            # Все, он больше не неуязвим, вернем ему нормальный спрайт.
        return


class Enemy(pygame.sprite.Sprite):
    # Стандартный класс врага.
    useless_image = pygame.transform.scale(load_image('Blank_image.png', -1),
                                           (int(width // 30), int(height // 16.875)))  # Гыыыыы.
    useless_image = crop(useless_image, -1)

    def __init__(self, speed, hp, value, base_dmg, base_freq, *group):
        super().__init__(*group)
        self.frost = 1
        self.base_freq = base_freq * fps
        self.base_dmg = base_dmg
        self.base_timing = 0
        self.image = Enemy.useless_image
        self.rect = self.image.get_rect()
        # Установка спрайта.
        self.curr_position = [i for i in road[0]]
        # Начальная позиция врага.
        self.target = 1
        # Номер вершины дороги, к которому должен идти враг.
        self.rect.topleft = (int(self.curr_position[0]), int(self.curr_position[1]))
        self.mask = pygame.mask.from_surface(self.image)
        # Маска врага для столкновений.
        self.hp = hp
        self.max_hp = hp
        # ХП врага.
        self.speed = speed * height / 1080 / fps
        # Перевод скорости из пикселей в секунду в пиксели в тик.
        self.value = value
        # Цена монстра (сколько денег игрок получит при его убийстве).
        return

    def update(self):
        if self.target == len(road):
            self.base_timing += 1
            if self.base_timing == self.base_freq:
                cursor.hp = max(cursor.hp - self.base_dmg, 0)
                sound = pygame.mixer.Sound('Data/hit.wav')
                sound.set_volume(0.3)
                pygame.mixer.Channel(1).play(sound)
                if cursor.hp == 0:
                    # Вызов экрана game-over.
                    game_over()
                self.base_timing = 0
        else:
            distance = self.speed * self.frost
            self.frost = 1
            # Учитываем замороженность и забываем ее.
            while distance >= 0.0000000000001 and self.target < len(road):
                # Обновляем врага, пока значеия не станут бессмысленными (спасибо погрешностям).
                dx = road[self.target][0] - self.curr_position[0]
                dy = road[self.target][1] - self.curr_position[1]
                distance_req = (dx * dx + dy * dy) ** 0.5
                if distance_req == 0:
                    self.target += 1
                    continue
                coefficient = min(distance / distance_req, 1)
                distance -= coefficient * distance_req
                if coefficient == 1:
                    self.target += 1
                self.curr_position[0] += dx * coefficient
                self.curr_position[1] += dy * coefficient
                # Умные переходы.
            self.rect.topleft = (int(self.curr_position[0]), int(self.curr_position[1]))
            # Все, обновили позицию.
        return

    def attack(self, damage):
        # Бьем врага.
        self.hp = max(self.hp - damage, 0)
        if self.hp == 0:
            self.curr_position = [-1000, -1000]
            self.rect.topleft = (int(self.curr_position[0]), int(self.curr_position[1]))
            # Тут тоже самое, как и с пулей.
            cursor.coins += self.value
            # Игрок получает прибыль!
        return

    def fire(self):
        # ВРАГ СТРЕЛЯЕТ!
        return

    def show_hp(self, surface):
        part = self.hp / self.max_hp
        pygame.draw.rect(surface, (255, 255, 255),
                         (self.curr_position[0], self.curr_position[1] - int(width / 120), int(width / 30), 8))
        pygame.draw.rect(surface, (0, 0, 0), (
            self.curr_position[0] + int(max(1, int(width / 30) * part)), self.curr_position[1] - int(width * 7 / 960),
            int((1 - part) * int(width / 30)), 5))
        # Отображение ХП врага.
        return

    def freeze(self, power):
        self.frost = min(power, self.frost)
        # Обновляем значение замороженности врага.
        return


class EnemyJack(Enemy):
    # Класс врага-Джека.
    jack_image = pygame.transform.scale(load_image('Jack.png', -1), (int(width // 30), int(height // 16.875)))
    jack_image = crop(jack_image, -1)

    def __init__(self, difficulty, *group):
        super().__init__(50, 500, 250, 20, 1, *group)
        self.image = EnemyJack.jack_image
        self.frequency = fps
        self.cooldown = fps
        # Он будет стрелять каждую секунду.

    def update(self):
        super().update()
        self.cooldown -= 1
        if self.cooldown <= 0:
            self.fire()
            # Стреляем, если пора стрелять.
            self.cooldown = self.frequency
        return

    def fire(self):
        directions = [[1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]]
        # Стреляем в восемь направлений.
        for direction in directions:
            enemy_bullets_list.append(Bullet([self.curr_position[0] + int(width / 80), self.curr_position[
                1] + int(width / 80)], 100, direction, 8, 200, 2 * fps, enemy_bullets))
        return


class EnemyRandom(Enemy):
    # Класс врага-кубика.
    random_image = pygame.transform.scale(load_image('Random.png', -1), (int(width // 30), int(height // 16.875)))
    random_image = crop(random_image, -1)

    def __init__(self, difficulty, *group):
        self.difficulty = difficulty
        super().__init__(random.randint(30, 50 + self.difficulty * 5), random.randint(
            100, 500 + self.difficulty * 400), random.randint(1, 5 + self.difficulty * 2) * 10, random.randint(
            1, 10 + self.difficulty * 2) * 5, random.randint(1, max(15 - self.difficulty, 3)), *group)
        # Рандомим характеристики согласно "сложности".
        self.image = EnemyRandom.random_image
        self.cooldown = fps * random.randint(1, max(3, 15 - random.randint(0, self.difficulty)))
        # Он будет стрелять рандомно. Совсем.

    def update(self):
        super().update()
        self.cooldown -= 1
        if self.cooldown <= 0:
            self.fire()
            # Стреляем, если пора стрелять.
            self.cooldown = fps * random.randint(1, max(3, 15 - random.randint(0, self.difficulty)))
        return

    def fire(self):
        bullets_amount = random.randint(1, 10 + self.difficulty)
        for i in range(bullets_amount):
            damage = random.randint(1, 10 + self.difficulty) * 5
            enemy_bullets_list.append(Bullet([self.curr_position[0] + int(width // 30 * 3 / 8), self.curr_position[
                1] + int(width // 30 * 3 / 8)], random.randint(int(width * 5 / 192),
                                                               int(width * 5 / 192) + self.difficulty * int(
                                                                   width / 96)), [math.sin(
                random.random() * 2 * math.pi), math.cos(
                random.random() * 2 * math.pi)], damage // 2, damage * 10, random.randint(
                1, 5 + self.difficulty) * fps, enemy_bullets))
        # Рандомим выстрел согласно "сложности".
        return


class TowerManager:
    # "Менеджер башен" - меню справа снизу для улучшения или удаления башни.

    def __init__(self, pos_x, pos_y, siz_x, siz_y):
        self.pos = [pos_x, pos_y]
        self.siz = [siz_x, siz_y]
        self.mid = siz_y // 2 + pos_y
        self.delete = smaller_font.render('DELETE', True, (255, 255, 255))
        # Запоминаем.
        return

    def render(self):
        if field.selected[0] != -1:
            # Отобразим меню, если есть выбранная башня.
            pygame.draw.rect(screen, (255, 255, 255), [self.pos[0], self.pos[1], self.siz[0], self.siz[1]], 2)
            cost = smaller_font.render(field.cells_data[field.selected[0]][field.selected[1]].cost, True, (
                255, 255, 255))
            screen.blit(cost, (self.pos[0] + 10, self.pos[1] + 10))
            pygame.draw.line(screen, (255, 255, 255), [self.pos[0], self.mid], [self.pos[0] + self.siz[0], self.mid], 2)
            screen.blit(self.delete, (self.pos[0] + 10, self.mid + 10))
        return

    def get_click(self, pos):
        if self.pos[0] <= pos[0] <= self.pos[0] + self.siz[0] and self.pos[1] <= pos[1] <= self.pos[1] + self.siz[
            1] and field.selected[0] != -1:
            # Проверим клик.
            if pos[1] >= self.mid:
                field.cells_data[field.selected[0]][field.selected[1]].rect = [-1000, -1000]
                field.cells_data[field.selected[0]][field.selected[1]].curr_position = [-1000, -1000]
                field.cells_data[field.selected[0]][field.selected[1]] = 0
                field.selected = [-1, -1]
                # Удалим башню.
            else:
                # Улучшим башню (вернее, попробуем).
                field.cells_data[field.selected[0]][field.selected[1]].upgrade()
        return


class Tower(pygame.sprite.Sprite):
    # Стандартный класс башни.
    useless_image = pygame.transform.scale(load_image('Tower_sample.png', -1), (int(width // 60), int(height // 33.75)))
    useless_image = crop(useless_image, -1)

    def __init__(self, cooldown, position, *group):
        super().__init__(*group)
        self.stage = 0
        self.cost = 'MAXED OUT'
        # Текущая цена.
        self.image = Tower.useless_image
        self.rect = self.image.get_rect()
        # Установка спрайта.
        self.curr_position = position
        # Позиция башни.
        self.rect.topleft = (int(self.curr_position[0]), int(self.curr_position[1]))
        self.cooldown = int(cooldown * fps)
        self.frequency = int(cooldown * fps)
        # Перевод времени в тики.
        return

    def update(self):
        self.cooldown -= 1
        if self.cooldown <= 0:
            self.cooldown = self.frequency
            self.fire()
        # Проверим, пора ли башне стрелять.
        return

    def fire(self):
        # Башня стреляет!
        return

    def upgrade(self):
        if self.cost[0] == 'M' or cursor.coins < int(self.cost[2:]):
            # Не будем улучшать, если у нее ужа макс. уровень, или у игрока слишком мало денег.
            return False
        cursor.coins -= int(self.cost[2:])
        self.cost = 'MAXED OUT'
        self.stage += 1
        sound = pygame.mixer.Sound('Data/installation.mp3')
        sound.set_volume(0.2)
        pygame.mixer.Channel(0).play(sound)
        # Улучшим башню и отобразим, что у нее макс. лвл.
        return True


class PlusTower(Tower):
    # Башня, быстро стреляющая слабыми пулями "плюсиком".
    tower_image = pygame.transform.scale(load_image('Plus_tower.png', -1), (int(width // 30), int(height // 16.875)))
    tower_image = crop(tower_image, -1)
    tower_image_ultra = pygame.transform.scale(load_image('Plus_tower_ultra.png', -1),
                                               (int(width // 30), int(height // 16.875)))
    tower_image_ultra = crop(tower_image_ultra, -1)

    def __init__(self, position, *group):
        super().__init__(0.333, position, *group)
        self.image = PlusTower.tower_image
        self.cost = '$ 100'
        return

    def fire(self):
        sound = pygame.mixer.Sound('Data/plus.wav')
        sound.set_volume(0.01)
        pygame.mixer.Channel(2).play(sound)
        if self.stage == 0:
            directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        else:
            directions = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, 1], [-1, -1], [1, -1]]
        # Будем стрелять в четыре или восемь направлений в зависимости от уровня башни.
        for direction in directions:
            k = 22
            if width == 1920:
                pass
            elif width == 1280:
                k = 10
            friendly_bullets_list.append(PlusBullet([self.curr_position[
                                                         0] + k, self.curr_position[
                                                         1] + k], 100,
                                                    direction, 10, 10, fps,
                                                    friendly_bullets))
        return

    def upgrade(self):
        if super().upgrade():
            self.image = PlusTower.tower_image_ultra

            sound = pygame.mixer.Sound('Data/installation.mp3')
            sound.set_volume(0.2)
            pygame.mixer.Channel(0).play(sound)
            # Обновим спрайт, если башня улучшена.
        return


class LaserTower(Tower):
    # Лазерная башня.
    tower_image = pygame.transform.scale(load_image('Laser_tower.png', -1), (int(width // 30), int(height // 16.875)))
    tower_image = crop(tower_image, -1)
    tower_image_ultra = pygame.transform.scale(load_image('Laser_tower_ultra.png', -1),
                                               (int(width // 30), int(height // 16.875)))
    tower_image_ultra = crop(tower_image_ultra, -1)

    def __init__(self, position, *group):
        super().__init__(-1, position, *group)
        self.image = LaserTower.tower_image
        self.range = 65536.5 * ((width / 1920) ** 2)
        self.damage = 60
        self.cost = '$ 200'
        self.target = None
        return

    def update(self):
        dist = 0
        if self.target is not None:
            dx = self.target.curr_position[0] - self.curr_position[0]
            dy = self.target.curr_position[1] - self.curr_position[1]
            dist = dx * dx + dy * dy
        if self.target is None or dist > self.range:
            best = None
            best_dist = self.range
            for curr_enemy in enemies_list:
                if curr_enemy.hp == 0:
                    continue
                dx = curr_enemy.curr_position[0] - self.curr_position[0]
                dy = curr_enemy.curr_position[1] - self.curr_position[1]
                dist = dx * dx + dy * dy
                if dist <= best_dist:
                    best_dist = dist
                    best = curr_enemy
            self.target = best
        # Тут мы ищем цель. Башня пытается либо продолжить стрелять во врага, либо переключиться на ближайшего.
        if self.target is not None:
            k = 32
            if width == 1280:
                k = 21
            if self.stage == 0:
                # Белый лазер - обычная башня наносит урон.
                sound1 = pygame.mixer.Sound('Data/laser.wav')
                sound1.set_volume(0.01)
                pygame.mixer.Channel(3).play(sound1)
                pygame.draw.line(screen, (128, 128, 128), [self.curr_position[0] + k, self.curr_position[1] + k], [
                    self.target.curr_position[0] + k, self.target.curr_position[1] + k], 5)
                self.target.attack(self.damage / fps)
            else:
                # Серый лазер - прокаченная башня останавливает врага.
                sound2 = pygame.mixer.Sound('Data/laser_stage2.wav')
                sound2.set_volume(0.01)
                pygame.mixer.Channel(6).play(sound2)
                self.target.freeze(0)
                pygame.draw.line(screen, (64, 64, 64), [self.curr_position[0] + k, self.curr_position[1] + k], [
                    self.target.curr_position[0] + k, self.target.curr_position[1] + k], 5)

        return

    def upgrade(self):
        if super().upgrade():
            self.image = LaserTower.tower_image_ultra
            self.range = 4096.5 * ((width / 1920) ** 2)
            sound = pygame.mixer.Sound('Data/installation.mp3')
            sound.set_volume(0.2)
            pygame.mixer.Channel(0).play(sound)
            # Обновим дальность, чтобы ее было проще контролировать.
        return


class FreezingTower(Tower):
    # Ледяная башня.
    tower_image = pygame.transform.scale(load_image('Freezing_tower.png', -1),
                                         (int(width // 30), int(height // 16.875)))
    tower_image = crop(tower_image, -1)
    tower_image_ultra = pygame.transform.scale(load_image('Freezing_tower_ultra.png', -1),
                                               (int(width // 30), int(height // 16.875)))
    tower_image_ultra = crop(tower_image_ultra, -1)

    def __init__(self, position, *group):
        super().__init__(-1, position, *group)
        self.image = FreezingTower.tower_image
        self.range = 16384 * ((width / 1920) ** 2)
        self.frost = 0.666
        self.damage = 20
        self.cost = '$ 50'
        return

    def update(self):
        for curr_enemy in enemies_list:
            # Переберем врагов.
            dx = curr_enemy.curr_position[0] - self.curr_position[0]
            dy = curr_enemy.curr_position[1] - self.curr_position[1]
            dist = dx * dx + dy * dy
            if dist <= self.range:
                curr_enemy.freeze(self.frost)
                # Если враг находится в диапазоне - замораживаем его.
                if self.stage == 1:
                    # Если башня прокачана, бьем врага.
                    curr_enemy.attack(self.damage / fps)
        return

    def upgrade(self):
        if super().upgrade():
            self.image = FreezingTower.tower_image_ultra
            self.frost = 0.5
            sound = pygame.mixer.Sound('Data/installation.mp3')
            sound.set_volume(0.2)
            pygame.mixer.Channel(0).play(sound)
            # Помимо спрайта, обновим силу мороза.
        return


class HomingTower(Tower):
    # Башня-снайпер с самонаведением.
    # Я придумал идею для норм. башни снайпера, но побоялся реализовать, так как, возможно, сильно бы нагружала игру.
    # Дело в том, что не получится применить формулу для определения положения врага, так как он может тормозиться
    # другими башнями.
    tower_image = pygame.transform.scale(load_image('Homing_tower.png', -1),
                                         (int(width // 30), int(height // 16.875)))
    tower_image = crop(tower_image, -1)
    tower_image_ultra = pygame.transform.scale(load_image('Homing_tower_ultra.png', -1),
                                               (int(width // 30), int(height // 16.875)))
    tower_image_ultra = crop(tower_image_ultra, -1)

    def __init__(self, position, *group):
        super().__init__(10, position, *group)
        self.image = HomingTower.tower_image
        self.cost = '$ 150'
        return

    def fire(self):
        targets = []
        if len(enemies_list) >= 2 and self.stage == 1:
            targets = random.sample(enemies_list, 2)
            # Если есть хотя бы два врага и башня прокачана - берем рандомные цели.
        elif len(enemies_list) >= 1:
            targets = random.sample(enemies_list, 1)
            # Если нет, но есть хотя бы один враг - берем рандомную цель.
        for target in targets:
            friendly_bullets_list.append(HomingBullet([
                self.curr_position[0] - int(width / 60), self.curr_position[1] - int(width / 60)], target,
                friendly_bullets))
            sound = pygame.mixer.Sound('Data/homing.wav')
            sound.set_volume(0.2)
            pygame.mixer.Channel(4).play(sound)
            # Стреляем!
        if len(targets) == 0:
            self.cooldown = 0
            # Если башня не нашла целей, ее кулдаун не сбросится.
        return

    def upgrade(self):
        if super().upgrade():
            self.image = HomingTower.tower_image_ultra
            self.frequency = 5 * fps
            sound = pygame.mixer.Sound('Data/installation.mp3')
            sound.set_volume(0.2)
            pygame.mixer.Channel(0).play(sound)
            # При улучшении мы также удваиваем скорость стрельбы.
        return


class Shop(Board):
    # Магазин.

    def __init__(self):
        super().__init__(5, 2, int(width / 30), 64, int(height - height * 23 / 135))
        self.products = [[0, 0], [PlusTower, 50], [LaserTower, 100], [FreezingTower, 100], [
            HomingTower, 150]]
        # Список товаров.
        self.descriptions = ['', '+', '-', '*', '~']
        # Список их символов.
        self.selected = 0
        return

    def on_click(self, cell):
        self.selected = cell[0]
        cursor.selected_tower = self.products[self.selected][0]
        # Выберем товар.
        return

    def render(self, surface):
        # Отобразим магазин.
        for i in range(self.columns):
            for j in range(self.rows):
                if self.selected == i:
                    # Выделенный товар мы... выделим.
                    pygame.draw.rect(surface, (255, 255, 255), (i * self.cell_size + self.indent[
                        0], j * self.cell_size + self.indent[1], self.cell_size, self.cell_size), 1)
                else:
                    # Иначе сделаем границы обычными.
                    pygame.draw.rect(surface, (64, 64, 64), (i * self.cell_size + self.indent[
                        0], j * self.cell_size + self.indent[1], self.cell_size, self.cell_size), 1)
                if j == 1 and self.products[i][1] != 0:
                    cost = smaller_font.render('$' + str(self.products[i][1]), True, (255, 255, 255))
                    screen.blit(cost, (self.indent[0] + i * self.cell_size + 5, self.indent[
                        1] + j * self.cell_size + 10))
                    # В нижней строке отобразим цену, если она не 0.
                elif j == 0:
                    cost = smaller_font.render(self.descriptions[i], True, (255, 255, 255))
                    screen.blit(cost, (self.indent[0] + i * self.cell_size + 10, self.indent[
                        1] + j * self.cell_size + 10))
                    # В верхней строке отобразим символ башни.
        return


class Spawner:
    # Спавнер спавнит врагов.

    def __init__(self, level_name):
        self.monster_types = [EnemyJack, EnemyRandom]
        # Типы монстров.
        level_data_file = open('levels\\' + level_name + '_enemies.txt')
        self.level_enemies_data = [[int(j) for j in i.split(':')] for i in level_data_file.read().split('\n')]
        # Считаем данные о монстрах из .txt-файла.
        for i in self.level_enemies_data:
            i[0] *= fps
            # Переводим секунды в тики.
        level_data_file.close()
        self.current_index = 0
        # Запомним, что сейчас должен спавниться моб №0.
        self.current_time = 0
        # Запомним, что пока прошло 0 тиков.
        return

    def update(self):
        self.current_time += 1
        # Обновим время.
        if self.current_time == self.level_enemies_data[self.current_index][0]:
            # Если подошло время - спавним врага.
            enemies_list.append(self.monster_types[self.level_enemies_data[self.current_index][1]](
                self.level_enemies_data[self.current_index][2], enemy_group))
            self.current_index += 1
            # Теперь нас волнует следующий враг.
            self.current_time = 0
            # Обновим время ождания.
        return


def game(level):
    global road, enemy_bullets_list, enemies_list, towers_list, friendly_bullets_list
    global font, smaller_font, cursor, shop, field
    font = pygame.font.Font('Data/pixelated.ttf', int(width * 5 / 192))
    smaller_font = pygame.font.Font('Data/pixelated.ttf', int(width / 65))
    # Шрифт я стырил с https://www.dafont.com/pixelated.font, мне сказали, что можно.
    road = []
    # Путь врага.
    field = Field(level)
    # А это поле.
    spawner = Spawner(level)
    # Отвечает за появление врагов.
    enemy_bullets_list = []
    # Здесь хранятся все "пули" врагов.
    cursor = Cursor(cursor_group)
    # Здесь - курсор.
    enemies_list = []
    # А здесь - враги.
    towers_list = []
    # Тут у нас башни.
    friendly_bullets_list = []
    # Тут - хорошие пули.
    shop = Shop()
    # Это магазин.
    base = pygame.sprite.Sprite()
    base.image = pygame.transform.scale(load_image('Base.png', -1), (int(width // 30), int(height // 16.875)))
    base.image = crop(base.image, -1)
    base.rect = base.image.get_rect()
    base.rect.topleft = [road[-1][0] + int(width // 30), road[-1][1]]
    base_group.add(base)
    # Отобразим базу.
    manager = TowerManager(int(width * 5 / 6), int(height - height * 23 / 135), int(width * 2 / 15),
                           int(height * 16 / 135))
    # Менеджер башен.
    running = True
    while running:
        for event in pygame.event.get():
            if overr or winn:
                running = False
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                    running = False
            elif event.type == pygame.MOUSEMOTION:
                # Крусор двигается.
                cursor.update(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                field.get_click(event.pos)
                shop.get_click(event.pos)
                manager.get_click(event.pos)
                # Проверим, кликнули ли мы на что-то важное.
        screen.fill((0, 0, 0))
        bullet_iter = 0
        while bullet_iter < len(enemy_bullets_list):
            # Цикл для вражеских пуль.
            current_bullet = enemy_bullets_list[bullet_iter]
            if current_bullet.update():
                del enemy_bullets_list[bullet_iter]
                # Удалим пулю, она не нужна.
            else:
                if pygame.sprite.collide_mask(current_bullet, cursor):
                    cursor.attack(current_bullet)
                    # Ударим курсор, если задели его.
                bullet_iter += 1
        enemy_iter = 0
        while enemy_iter < len(enemies_list):
            # Цикл для врагов.
            current_enemy = enemies_list[enemy_iter]
            if current_enemy.hp == 0:
                sound = pygame.mixer.Sound('Data/death.wav')
                sound.set_volume(0.3)
                pygame.mixer.Channel(5).play(sound)

                del enemies_list[enemy_iter]
                # Удалим врага, если он умер.
            else:
                current_enemy.update()
                enemy_iter += 1
        bullet_iter = 0
        while bullet_iter < len(friendly_bullets_list):
            # Цикл для хороших пуль.
            current_bullet = friendly_bullets_list[bullet_iter]
            if current_bullet.update():
                del friendly_bullets_list[bullet_iter]
                # Удалим пулю, она не нужна.
            else:
                attacked = False
                for enemy in enemies_list:
                    if pygame.sprite.collide_mask(current_bullet, enemy):
                        enemy.attack(current_bullet.damage)
                        current_bullet.current_position = [-1000, -1000]
                        current_bullet.rect.topleft = (int(
                            current_bullet.current_position[0]), int(current_bullet.current_position[1]))
                        del friendly_bullets_list[bullet_iter]
                        attacked = True
                        break
                if not attacked:
                    bullet_iter += 1
        if cursor.invincible:
            cursor.update_invincibility()
            # Обновим неуязвимость курсора, если он неуязвим.
        if spawner.current_index != len(spawner.level_enemies_data):
            spawner.update()
        elif len(enemies_list) == 0:
            # Вызов экрана победы.
            win()
            break
        hp_hud = font.render('<3   ' + str(cursor.hp), True, (255, 255, 255))
        screen.blit(hp_hud, (int(width * 0.4), int(height - height * 23 / 135)))
        coins_hud = font.render('   $      ' + str(cursor.coins), True, (255, 255, 255))
        screen.blit(coins_hud, (int(width * 0.4), int(height - height / 9)))
        shop.render(screen)
        manager.render()
        towers_group.draw(screen)
        field.render(screen)
        cursor_group.draw(screen)
        tower_iter = 0
        while tower_iter < len(towers_list):
            current_tower = towers_list[tower_iter]
            if current_tower.curr_position[0] == -1000:
                del towers_list[tower_iter]
            else:
                current_tower.update()
                tower_iter += 1
        # Похожая схема с башнями.
        enemy_group.draw(screen)
        friendly_bullets.draw(screen)
        for current_enemy in enemies_list:
            current_enemy.show_hp(screen)
        enemy_bullets.draw(screen)
        base_group.draw(screen)
        pygame.display.flip()
        # Обновим экран.
        fps_clock.tick(fps)
        # Тик.


def game_over():
    # Функция экрана game-over.
    global overr, running
    running = False
    overr = True
    width, height = size
    screen = pygame.display.set_mode((width, height))
    screen.fill((0, 0, 0))
    image = [0, 0, 0, 0]
    image[0] = load_image('Game_over.png')
    image[1] = image[0].get_rect(centerx=width / 2, centery=height / 2)
    image[2] = load_image('PressA.png')
    image[3] = image[2].get_rect(centerx=width / 1.97, centery=height * 0.9)
    screen.blit(image[0], image[1])
    screen.blit(image[2], image[3])

    pygame.display.update()

    pygame.mixer.music.load('Data/game-over.wav')
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play()

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    run = False
    main_menu()


def win():
    # Функция экрана победы.
    global winn, running
    running = False
    winn = True
    width, height = size
    screen.fill((0, 0, 0))
    image = [0, 0, 0, 0]
    image[0] = load_image('Win.png')
    image[1] = image[0].get_rect(centerx=width / 2, centery=height / 2)
    image[2] = load_image('PressA.png')
    image[3] = image[2].get_rect(centerx=width / 1.97, centery=height * 0.9)
    screen.blit(image[0], image[1])
    screen.blit(image[2], image[3])

    pygame.display.update()
    pygame.mixer.music.load('Data/you-win.wav')
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play()

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    run = False
    main_menu()


def main_menu():
    # А здесь снова враги.
    background = pygame.Surface(size)
    res_win.main_window()
    if res_win.levels():
        SelectMap.level_window()
        lvl = SelectMap.Game_level()
        if SelectMap.running():
            # Очищаем спрайты.
            for item in towers_group:
                item.kill()
                towers_group.clear(screen, background)
                towers_group.draw(screen)
            for item in cursor_group:
                item.kill()
                cursor_group.clear(screen, background)
                cursor_group.draw(screen)
            for item in enemy_group:
                item.kill()
                enemy_group.clear(screen, background)
                enemy_group.draw(screen)
            for item in friendly_bullets:
                item.kill()
                friendly_bullets.clear(screen, background)
                friendly_bullets.draw(screen)
            for item in enemy_bullets:
                item.kill()
                enemy_bullets.clear(screen, background)
                enemy_bullets.draw(screen)
            for item in base_group:
                item.kill()
                base_group.clear(screen, background)
                base_group.draw(screen)
            # Отключаем видимость курсора, чтобы был только наш в игре.
            pygame.mouse.set_visible(False)
            global overr, winn
            overr = False
            winn = False
            game(lvl)
        else:
            main_menu()
    elif res_win.Options():
        # Вызываем окно настроек.
        OptionsWindow.options_window(pygame.time.Clock(), size)
        if not OptionsWindow.running():
            main_menu()


if __name__ == '__main__':
    main_menu()