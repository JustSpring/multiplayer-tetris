class Shape:
    def __init__(self,arr,color):
        self.allPositions=arr
        self.color=color
    def getShape(self,rotation):
        return self.allPositions[rotation]

line = [
    [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0]],
    [[0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0]],
    [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]]
]
square = [
    [[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]],
    [[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]],
    [[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]],
    [[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]]
]
t = [
    [[0, 0, 0, 0], [0, 1, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0]],
    [[0, 1, 0, 0], [0, 1, 1, 0], [0, 1, 0, 0], [0, 0, 0, 0]],
    [[0, 0, 0, 0], [1, 1, 1, 0], [0, 1, 0, 0], [0, 0, 0, 0]],
    [[0, 1, 0, 0], [1, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0]]
]
s = [
    [[0, 0, 0, 0], [0, 1, 1, 0], [1, 1, 0, 0], [0, 0, 0, 0]],
    [[0, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 0], [0, 0, 0, 0]],
    [[0, 0, 0, 0], [0, 1, 1, 0], [1, 1, 0, 0], [0, 0, 0, 0]],
    [[0, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 0], [0, 0, 0, 0]]
]
z = [
    [[0, 0, 0, 0], [1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0]],
    [[0, 0, 1, 0], [0, 1, 1, 0], [0, 1, 0, 0], [0, 0, 0, 0]],
    [[0, 0, 0, 0], [1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0]],
    [[0, 0, 1, 0], [0, 1, 1, 0], [0, 1, 0, 0], [0, 0, 0, 0]]
]
j = [
    [[1, 0, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[0, 1, 1, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0]],
    [[0, 0, 0, 0], [1, 1, 1, 0], [0, 0, 1, 0], [0, 0, 0, 0]],
    [[0, 1, 0, 0], [0, 1, 0, 0], [1, 1, 0, 0], [0, 0, 0, 0]]
]
l = [
    [[0, 0, 1, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0]],
    [[0, 0, 0, 0], [1, 1, 1, 0], [1, 0, 0, 0], [0, 0, 0, 0]],
    [[1, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0]]
]

shapes = [
    Shape(line, 1),
    Shape(square, 4),
    Shape(t, 6),
    Shape(s, 5),
    Shape(z, 7),
    Shape(j, 2),
    Shape(l, 3)
]

names = [
    "Briella Black", "Zahir Avery", "Meghan Pena", "Marcus Boone", "Mariam Watkins",
    "Nash Fisher", "Arya Hardin", "Hassan Cohen", "Destiny Moss", "Porter Taylor",
    "Sofia Dickson", "Flynn Maddox", "Zainab Castel", "Kai Meyer", "Sara Payne",
    "Edward Baldwi", "Esmeralda Par", "Karsyn Sutton", "Izabella Shep", "Ronald Strong",
    "Margo Lang", "Wells Kelly", "Ruby Barry", "Emery Randall", "Christina Ber",
    "Jair McCann", "Joyce Cobb", "Raphael Dean", "Julianna Madde", "Everest Kelle",
    "Rosalie Santi", "Beckham Montg", "Eva Guzman", "Jude Buck", "Livia Donovan",
    "Brayan Marin", "Celia Marshal", "Kaiden McCall", "Kai Cummings", "Raiden Woodwd",
    "Drew Harper", "Hayes Vasquez", "Rose Harrison", "Gavin Mayer", "Ainhoa Huber",
    "Mac Warren", "Sloane Gray", "Nicholas Rome", "Eliza Vang", "Jimmy Gaines",
    "Aya Dunn", "Dawson Skinner", "Mara Giles", "Kole Bowers", "Elisa Nichols",
    "Atlas Ortiz", "Anna Raymond", "Maurice Giles", "Bailee Gray", "Nicholas Ward",
    "Ariana Archer", "Ephraim Lam", "Karina Peck", "Yousef Gutier", "Savannah Grif",
    "Ayden Truong", "Judith Bryan", "Jaxtyn Hendri", "Zhuri Klein", "Marco Morris",
    "Genesis Littl", "Lennox Newman", "Oaklynn Morto", "Roland McCart", "Kira Suarez",
    "Soren Hebert", "Kyleigh Finle", "Calum Bender", "Lilyana Huff", "Finnley Kramer",
    "Hanna Rich", "Miller Willia", "Ava Carr", "Kash Correa", "Valery Carey",
    "Watson Jeffe", "Julieta Dudle", "Colter Macdon", "Rosalia Pierce", "Nicolas Port",
    "Ryleigh Hodge", "Reign Powell", "Vivian Aceved", "Dakari Bradsh", "Berkley Princ",
    "Aron Wilson", "Luna Madden", "Everest Allis", "Chelsea Campo", "Gideon Meza"
]