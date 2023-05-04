from pygame.math import Vector2 as Vector

rect_layout = []
circle_layout = []

"""Набор 1"""

RECT_OBSTACLES_1 = [
    [200, 350, 400, 50],
    [0, 600, 150, 30],
    [650, 600, 150, 30],
    [450, 0, 20, 350]
]
CIRCLE_OBSTACLES_1 = [
    {"pos": Vector(200, 250), "radius": 50, "strength": 0.5},
    {"pos": Vector(400, 450), "radius": 30, "strength": 0.5},
    {"pos": Vector(300, 450), "radius": 20, "strength": 0.3},
    {"pos": Vector(500, 150), "radius": 15, "strength": 0.4},
    {"pos": Vector(600, 200), "radius": 60, "strength": 0.4}
]

rect_layout.append(RECT_OBSTACLES_1)
circle_layout.append(CIRCLE_OBSTACLES_1)


"""Набор 2"""

RECT_OBSTACLES_2 = [
    [200, 250, 400, 50],
    [0, 475, 200, 30],
    [600, 475, 200, 30],
]
CIRCLE_OBSTACLES_2 = []

rect_layout.append(RECT_OBSTACLES_2)
circle_layout.append(CIRCLE_OBSTACLES_2)


"""Набор 3"""

RECT_OBSTACLES_3 = []
CIRCLE_OBSTACLES_3 = [
    {"pos": Vector(640, 200), "radius": 50, "strength": 0.6},
    {"pos": Vector(450, 380), "radius": 150, "strength": 1.5},
    {"pos": Vector(700, 400), "radius": 25, "strength": 0.3},
    {"pos": Vector(320, 100), "radius": 20, "strength": 0.3},
    {"pos": Vector(185, 265), "radius": 70, "strength": 0.8},
    {"pos": Vector(100, 550), "radius": 40, "strength": 0.3}
]

rect_layout.append(RECT_OBSTACLES_3)
circle_layout.append(CIRCLE_OBSTACLES_3)


"""Набор 4"""

RECT_OBSTACLES_4 = [
    [0, 500, 500, 30],
    [400, 300, 400, 30],
    [0, 300, 160, 100],
    [200, 0, 30, 200],
    [420, 0, 30, 100]
]
CIRCLE_OBSTACLES_4 = [
    {"pos": Vector(350, 350), "radius": 40, "strength": 0.3},

]

rect_layout.append(RECT_OBSTACLES_4)
circle_layout.append(CIRCLE_OBSTACLES_4)
