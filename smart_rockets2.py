import random
import time
import math
from math import atan2, cos, sin

import pygame
import pygame.gfxdraw
from pygame.math import Vector2 as Vector

import pygame_widgets
from pygame_widgets.button import Button  # Кнопка
from pygame_widgets.slider import Slider  # Ползунок
from pygame_widgets.textbox import TextBox  # Текст

from radiobutton import Checkbox  # Радиокнопка
from layouts import rect_layout, circle_layout

pygame.init()
random.seed(time.time())

WIDTH = 800
HEIGHT = 800

BACKGROUND = (0, 0, 0)

COUNT = 0
TARGET = Vector(WIDTH / 2, 50)
SPAWNPOINT = WIDTH / 2, HEIGHT - 100

MAXFORCE = 1  # Сила двигателя #TODO: Изменить значения для большей наглядности
GRAVITY_CONSTANT = 30  # Гравитационная постоянная
MASS = 4  # Масса ракеты

current_settings = {
    'POPULATION': 500,  # Размер популяции
    'LIFESPAN': 500,  # Время жизни
    'MUTATION': 0.05,  # Изн. вер. мутации
    'FPS': 240,  # Скорость симуляции
    'RECT_layout': rect_layout[0],
    'CIRCLE_layout': circle_layout[0]

}
settings_menu_open = False


def random_vector(magnitude=1):
    # Генерирует случайное направление и скорость
    """
    x = random.random()
    if (random.random() > 0.5):
        x *= -1
    y = random.random()
    if (random.random() > 0.5):
        y *= -1
    return Vector(x=x, y=y)
    """

    # Генерирует вектор с постоянной скоростью и случайным направлением
    phi = 2 * math.pi * random.random()
    vx = magnitude * cos(phi)
    vy = magnitude * sin(phi)

    return Vector(x=vx, y=vy)


def settingsMenu():  # Меню настроек
    global settings_menu_open
    if settings_menu_open:
        slider_population.show()
        slider_lifespan.show()
        slider_mutation.show()
        fps_input.show()
    else:
        slider_population.hide()
        slider_lifespan.hide()
        slider_mutation.hide()
        fps_input.hide()

    settings_menu_open = not settings_menu_open


def fullrestart():  # TODO: сделать чтобы параметры можно было менять в реальном времени
    global COUNT, current_settings, population, start_time
    COUNT = 0
    current_settings["POPULATION"] = slider_population.getValue()  # Обновление настроек
    current_settings["LIFESPAN"] = slider_lifespan.getValue()
    current_settings["MUTATION"] = slider_mutation.getValue()
    if int(fps_input.getText()) >= 10:
        current_settings["FPS"] = int(fps_input.getText())
    else:
        current_settings["FPS"] = 10
        fps_input.setText(10)
    for i in range(len(boxes)):
        if boxes[i].checked:
            current_settings['RECT_layout'] = rect_layout[i]
            current_settings['CIRCLE_layout'] = circle_layout[i]
            break
    population = Population()
    start_time = time.time()
    print("----- Перезапуск с новыми параметрами -----\n")


class Population:

    def __init__(self):
        self.rockets = []
        self.popsize = current_settings.get("POPULATION")  # 500
        self.generation = 1
        self.maxscore = 0
        self.avgscore = 0
        self.stdDevScore = 0
        self.matingpool = []
        self.best_rocket = None

        self.rockets = [Rocket(None) for i in range(self.popsize)]

    def evaluate(self):

        maxfit = 0
        runningsum = 0

        # Подсчёт значений пригодности и определение лучшей ракеты
        for rocket in self.rockets:
            rocket.calcFitness()
            if rocket.fitness > maxfit:
                maxfit = rocket.fitness
                self.best_rocket = rocket

        # Вычисление статистических данных
        self.avgscore = '%.6f' % (sum(r.fitness for r in self.rockets) / len(self.rockets))
        self.maxscore = '%.6f' % maxfit
        for rocket in self.rockets:
            runningsum += (rocket.fitness - float(self.avgscore)) ** 2
        self.stdDevScore = '%.6f' % (math.sqrt(runningsum / len(self.rockets)))

        # Вывод статистических данных #TODO: реализовать вывод в csv файл
        print(f"Поколение: {self.generation}\n"
              f"Наибольшая приспособленность: {self.maxscore}\n"
              f"Средняя приспособленность: {self.avgscore}\n"
              f"Среднеквадратичное отклонение приспособленности: {self.stdDevScore}")
        if self.best_rocket.completed:
            print(f"Наилучшее кол-во шагов: {self.best_rocket.count}")
        else:
            print(f"Наилучшее кол-во шагов: {current_settings.get('LIFESPAN')}")
        print("Прошло времени:", current_time_str, "\n")
        """
        print(self.generation, self.maxscore, self.avgscore, self.stdDevScore, self.best_rocket.count, current_time_str)
        if self.best_rocket.completed:
            pass
        else:
            print(current_settings.get('LIFESPAN'))"""
        # Нормировать значения в диапазоне 0-1
        for rocket in self.rockets:
            rocket.fitness /= maxfit

        self.matingpool = []
        for rocket in self.rockets:
            n = rocket.fitness * 100  # Кол-во потомков
            for j in range(int(n)):
                self.matingpool.append(rocket)

    def selection(self):

        newRockets = []

        for i in range(len(self.rockets)):
            # Получить ДНК двух случайных родителей
            parentA = random.choice(self.matingpool).dna
            parentB = random.choice(self.matingpool).dna

            # ДНК объект
            child = parentA.crossover(parentB)
            child.mutation()
            newRockets.append(Rocket(child))

        self.rockets = newRockets
        self.best_rocket.color = (69, 205, 247)
        self.best_rocket.reset()
        self.rockets.append(self.best_rocket)

    def run(self, screen1):
        for i, rocket in enumerate(self.rockets):
            rocket.update()
            rocket.show(screen1)


class DNA:

    def __init__(self, gene_o=None):
        self.genes = []

        if gene_o:
            self.genes = gene_o
        else:
            for i in range(current_settings.get("LIFESPAN")):
                self.genes.append(random_vector(MAXFORCE))

    def crossover(self, partner):

        newgenes = []
        mid = random.randint(0, len(self.genes))
        for i in range(len(self.genes)):
            # Если i > mid, взять гены из оригинальной ДНК
            if i > mid:
                newgenes.append(self.genes[i])
            # Иначе если i =< mid, взять гены от партнера
            else:
                newgenes.append(partner.genes[i])
        return DNA(newgenes)

    def mutation(self):

        for i in range(len(self.genes)):
            if random.random() < current_settings.get("MUTATION"):
                self.genes[i] = random_vector(MAXFORCE)


class Rocket:

    def __init__(self, dna=None):
        self.mass = MASS
        self.pos = Vector(SPAWNPOINT)
        self.vel = Vector()
        self.acc = Vector()
        if dna is None:
            self.dna = DNA()
        else:
            self.dna = dna
        self.fitness = 0
        self.completed = False
        self.crashed = False
        self.path = []
        self.closest_to_finish = 10000

        self.count = 0
        self.color = (255, 255, 255)

    def reset(self):
        self.pos = Vector(SPAWNPOINT)
        self.vel = Vector()
        self.acc = Vector()
        self.fitness = 0
        self.completed, self.crashed = False, False
        self.count = 0
        self.path = []
        self.closest_to_finish = 10000

    def applyForce(self, force):
        self.acc += force / self.mass

    def calcFitness(self):
        if self.completed:
            self.fitness = 1.0 / 16.0 + 10000 / (self.count ** 2)  # Приспособленность в случае успеха
        elif self.crashed:
            self.fitness = 1 / (self.closest_to_finish ** 3)  # Приспособленность в случае провала
        else:
            self.fitness = 1 / (self.closest_to_finish ** 2)  # Приспособленность в иных случаях

    def update(self):

        d = math.sqrt(((self.pos.x - TARGET.x) ** 2) + ((self.pos.y - TARGET.y) ** 2))
        if d < 10:
            self.completed = True
            self.pos.x, self.pos.y = TARGET.x, TARGET.y
            return

        # Если ракета попала в прямоугольное препятствие
        for rect in current_settings.get("RECT_layout"):
            if (rect[0] < self.pos.x < rect[0] + rect[2]) \
                    and (rect[1] < self.pos.y < rect[1] + rect[3]):
                self.crashed = True
                return

        # Если ракета вышла за пределы рабочей зоны
        if (self.pos.x < 0 or self.pos.x > WIDTH) or (self.pos.y < 0 or self.pos.y > HEIGHT):
            self.crashed = True
            return

        for circle in current_settings.get("CIRCLE_layout"):
            obstacle_pos = pygame.Vector2(circle["pos"])
            obstacle_radius = circle["radius"]
            dist = self.pos.distance_to(obstacle_pos)  # Расстояние между ракетой и препятствием
            if dist < obstacle_radius:
                self.crashed = True
                return
            force = GRAVITY_CONSTANT * self.mass * obstacle_radius / (dist ** 2)  # Формула для расчета силы
            direction = (obstacle_pos - self.pos).normalize()  # Направление вектора силы
            acceleration = force / self.mass  # Расчет ускорения ракеты
            self.vel += acceleration * direction  # Изменение скорости ракеты

        # Обновление положения и скорости ракеты
        self.pos += self.vel

        if COUNT < current_settings.get("LIFESPAN"):
            self.applyForce(self.dna.genes[COUNT])

        if not self.completed and not self.crashed:
            self.vel += self.acc
            self.pos += self.vel
            self.acc *= 0
            self.count += 1
            if self.pos.distance_to(TARGET) < self.closest_to_finish:
                self.closest_to_finish = self.pos.distance_to(TARGET)

    def show(self, screen1):

        width = 2
        length = 12

        angle = atan2(self.vel.y, self.vel.x)  # Угол под которым отображается ракета

        # Основные точки для прямоугольника вокруг центра ракеты
        points = [
            [self.pos.x - length, self.pos.y - width],
            [self.pos.x + length, self.pos.y - width],
            [self.pos.x + length, self.pos.y + width],
            [self.pos.x - length, self.pos.y + width],
        ]

        for i, point in enumerate(points):
            # Повернуть точки вокруг центра ракеты (x,y)
            points[i] = [int((point[0] - self.pos.x) * cos(angle) - (point[1] - self.pos.y) * sin(angle)) + self.pos.x,
                         int((point[0] - self.pos.x) * sin(angle) + (point[1] - self.pos.y) * cos(angle)) + self.pos.y]

        # pygame.gfxdraw.aapolygon(screen1, points, self.color)
        pygame.draw.polygon(screen1, self.color, points)
        pygame.gfxdraw.polygon(screen1, points, (200, 200, 200))


screen1 = pygame.display.set_mode([WIDTH, HEIGHT])  # Окно симуляции
pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN])

clock = pygame.time.Clock()
pygame.display.set_caption("Smart Rockets")

'''ВИДЖЕТЫ'''

pygame.font.init()  # Инициализация шрифтов
font = pygame.font.SysFont('Verdana', 14)  # Создание шрифта

image1 = pygame.image.load("config.png").convert()
image2 = pygame.image.load("reset.png").convert()

settingsButton = Button(screen1, 750, 00, 50, 50,
                        image=image1, inactiveColour=(0, 0, 0), pressedColour=(0, 0, 0), hoverColour=(0, 0, 0),
                        onRelease=settingsMenu)
resetButton = Button(screen1, 750, 60, 50, 50,
                     image=image2, inactiveColour=(0, 0, 0), pressedColour=(0, 0, 0), hoverColour=(0, 0, 0),
                     onRelease=fullrestart)
slider_population = Slider(screen1, 600, 10, 120, 10, min=50, max=3000, step=10,
                           handleColour=(88, 148, 156), initial=current_settings.get("POPULATION"))
slider_lifespan = Slider(screen1, 600, 30, 120, 10, min=100, max=999, step=10,
                         handleColour=(88, 148, 156), initial=current_settings.get("LIFESPAN"))
slider_mutation = Slider(screen1, 600, 50, 120, 10, min=0.00, max=1.00, step=0.01,
                         handleColour=(88, 148, 156), initial=current_settings.get("MUTATION"))
fps_input = TextBox(screen1, 610, 65, 40, 30, font=font)
fps_input.setText(current_settings.get("FPS"))

boxes = []
button1 = Checkbox(screen1, 600, 100, 0, caption='1')
button1.checked = True  # Первый набор препятствий
button2 = Checkbox(screen1, 625, 100, 1, caption='2')
button3 = Checkbox(screen1, 650, 100, 2, caption='3')
button4 = Checkbox(screen1, 675, 100, 3, caption='4')
boxes.append(button1)
boxes.append(button2)
boxes.append(button3)
boxes.append(button4)

settingsMenu()  # Вызов, чтобы спрятать ползунки

''' Основной цикл '''

rocket = Rocket()
population = Population()
start_time = time.time()
running = 1
while running:

    clock.tick(current_settings.get("FPS"))
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:  # Выход
            pygame.quit()
            running = 0
            quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            for box in boxes:
                box.update_checkbox(event)
                if box.checked is True:
                    for b in boxes:
                        if b != box:
                            b.checked = False

    screen1.fill(BACKGROUND)

    # Отрисовка цели
    pygame.gfxdraw.aacircle(screen1, int(TARGET.x), int(TARGET.y), 16, (69, 247, 125))
    pygame.draw.circle(screen1, (69, 247, 125), (int(TARGET.x), int(TARGET.y)), 16, 2)
    population.run(screen1)

    # Отрисовка препятствий
    for rectangle in current_settings.get("RECT_layout"):
        pygame.gfxdraw.rectangle(screen1, rectangle, (247, 69, 69))

    for circle in current_settings.get("CIRCLE_layout"):
        obstacle_pos = circle["pos"]
        obstacle_radius = circle["radius"]
        pygame.draw.circle(screen1, (66, 135, 245), obstacle_pos, obstacle_radius, 2)

    current_time = time.time() - start_time
    current_time_str = time.strftime('%H:%M:%S', time.gmtime(current_time))

    pygame.display.set_caption(
        f"Умные ракеты | Поколение: {population.generation} "
        f"| Шаг: {COUNT:<3} "
        f"| Времени с запуска: {current_time_str}")
    COUNT += 1

    if COUNT >= current_settings.get("LIFESPAN"):
        population.evaluate()
        population.selection()
        population.generation += 1
        # population = Population() #Перезапуск
        COUNT = 0

    # Добавление текущей позиции в путь
    if population.best_rocket is not None:
        population.best_rocket.path.append(population.best_rocket.pos.copy())
        # Отрисовка пути лучшей ракеты
    if population.best_rocket is not None and len(population.best_rocket.path) > 1:
        pygame.draw.lines(screen1, (0, 255, 0), False, population.best_rocket.path, 2)

    label_population = font.render("Размер популяции:" + str(slider_population.getValue()), True, (255, 255, 255))
    label_lifespan = font.render("Время цикла:" + str(slider_lifespan.getValue()), True, (255, 255, 255))
    label_mutation = font.render("Мутация:" + str(int(slider_mutation.getValue() * 100)) + "%", True, (255, 255, 255))
    label_fps = font.render("FPS:", True, (255, 255, 255))
    label_layout = font.render("Набор препятствий:", True, (255, 255, 255))

    slider_population.listen(events)
    slider_lifespan.listen(events)
    slider_mutation.listen(events)

    if settings_menu_open:
        label_population.set_alpha(0)
        label_lifespan.set_alpha(0)
        label_mutation.set_alpha(0)
        label_fps.set_alpha(0)
        label_layout.set_alpha(0)
    else:  # Отрисовка элементов настроек
        label_population.set_alpha(255)
        label_lifespan.set_alpha(255)
        label_mutation.set_alpha(255)
        label_fps.set_alpha(255)
        label_layout.set_alpha(255)
        for box in boxes:
            box.render_checkbox()
        screen1.blit(label_population, (slider_population.getX() - 185, slider_population.getY() - 5))
        screen1.blit(label_lifespan, (slider_lifespan.getX() - 145, slider_lifespan.getY() - 5))
        screen1.blit(label_mutation, (slider_mutation.getX() - 115, slider_mutation.getY() - 5))
        screen1.blit(label_fps, (fps_input.getX() - 40, fps_input.getY() + 5))
        screen1.blit(label_layout, (button1.x - 155, button1.y))

    pygame_widgets.update(events)
    pygame.display.update()

pygame.quit()
