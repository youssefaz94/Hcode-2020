import multiprocessing
import heapq
import math
from utils import timeit

class GlobalData:
    def __init__(self):
        self.map = {}
    def set_v(self, name, value):
        self.map[name] = value
    def get_v(self, name):
        return self.map.get(name)

class Library:
    def __init__(self, id, signup, shipping_rate, gd):
        self.id = id
        self.signup = signup
        self.shipping_rate = shipping_rate
        self.gd = gd

    def get_all_books_days(self):
        return math.ceil(len(self.books)/self.shipping_rate)

    def operating_days(self):
        total_books = self.get_all_books_days()
        possible_work_days = max(0, self.gd.get_v('days_left')-self.signup)
        return min(total_books, possible_work_days)
    
    def wasted_days(self):
        possible_work_days = max(0, self.gd.get_v('days_left')-self.signup)
        return max(0, possible_work_days - self.operating_days())

    def burn_books(self):
        for book in self.concerned_books:
            book.burn()

    @property
    def books(self):
        return self._books

    @books.setter
    def books(self, books):
        self._books = sorted(books, reverse=True)
        self.layout_changed = True

    def order_books(self):
        self._books = list(filter(lambda x: x.value != 0, self._books))
        nbr_possible_books = self.operating_days()*self.shipping_rate
        self.concerned_books = self._books[:nbr_possible_books]
        self.layout_changed = False
    
    def lib_value(self):
        if self.layout_changed:
            self.order_books()
        value = 0
        for book in self.concerned_books:
            value += book.value
        return value

    def sort_equation(self):
        return self.lib_value()/self.signup
    
    def __repr__(self):
        return 'Library(id: {}, signup: {} \n books: {})'.format(self.id, self.signup, self.books)
    
    def __lt__(self, value):
        return self.sort_equation() > value.sort_equation()

class Book:
    def __init__(self, id, value, gd):
        self.id = id
        self.value = value
        self.libraries = set()
        self.gd = gd

    def add_library(self, lib):
        self.libraries.add(lib)
        return self

    def burn(self):
        self.value = 0
        for lib in self.libraries:
            lib.layout_changed = True
    
    def __repr__(self):
        return 'Book(id: {}, value: {})'.format(self.id, self.value)
    
    def __lt__(self, value):
        return self.value < value.value



@timeit
def main(gd):
    books = gd.get_v('books')
    libraries = gd.get_v('libraries')
    final_result = []
    while libraries:
        library = heapq.heappop(libraries)
        if library.lib_value() == 0:
            break
        final_result.append(library)
        library.burn_books()
        heapq.heapify(libraries)
    return final_result


def multip(file):
    gd = GlobalData()
    with open('./inputs/{}'.format(file)) as f:
        gd.set_v('file', file)
        line = f.readline()
        tot_nbr_books, tot_nbr_lib, tot_nbr_days = list(map(int, line.strip().split()))
        gd.set_v('tot_nbr_books', tot_nbr_books)
        gd.set_v('tot_nbr_lib', tot_nbr_lib)
        gd.set_v('tot_nbr_days', tot_nbr_days)
        gd.set_v('days_left', tot_nbr_days)

        line = f.readline()
        books = {}
        gd.set_v('books', books)
        for id, value in enumerate(list(map(int, line.strip().split()))):
            book = Book(id, value, gd)
            books[id] = book

        libraries = []
        gd.set_v('libraries', libraries)
        for i in range(tot_nbr_lib):
            line = f.readline()
            _, signup, shipping_rate = list(map(int, line.strip().split()))
            library = Library(i, signup, shipping_rate, gd)
            line = f.readline()
            library.books = list(map(lambda x: books[int(x)].add_library(library), line.strip().split()))
            heapq.heappush(libraries, library)
    
    result = main(gd)

    with open('./outputs/{}'.format(gd.get_v('file')), 'w+') as f:
        line = '{}\n'.format(len(result))
        f.write(line)
        for i in result:
            line = '{} {}\n'.format(i.id, len(i.concerned_books))
            f.write(line)
            line = ' '.join(map(lambda x: str(x.id), i.concerned_books))
            f.write(line+'\n')
    
    print("complete ", gd.get_v('file'))

if __name__ == "__main__":
    files = ['a_example.txt', 'b_read_on.txt', 'c_incunabula.txt', 'd_tough_choices.txt', 'e_so_many_books.txt', 'f_libraries_of_the_world.txt']
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pool.map(multip, files)