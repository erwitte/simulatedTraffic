class Person:
    id = ""
    home_location = []
    workplace = []
    free_time_places = []

    def __init__(self, id, home_location, workplace, free_time_places):
        self.id = id
        self.home_location = home_location
        self.workplace = workplace
        self.free_time_places = free_time_places
        self.times = []
        self.coords = []
        # index 0 = home_location, index = 1 workplace, index 2 = free_time_places(1), index 3 = free_time_places(2)
        self.indices = [None for _ in range(4)]

    def fill_arrays(self, coords, times, i):
        if coords == self.home_location:
            self.indices[0] = i
        if coords == self.workplace:
            self.indices[1] = i
        if coords == self.free_time_places[0]:
            self.indices[2] = i
        if coords == self.free_time_places[1]:
            self.indices[3] = i
        self.coords.append([coords[0], coords[1]])
        self.times.append(times)
