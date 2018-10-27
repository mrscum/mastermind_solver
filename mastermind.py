import itertools
import random
import optparse
import sys

COLOURS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

parser = optparse.OptionParser()
parser.add_option('-c', '--colours', dest = "colours", help = "Number of colours available", type = "int")
parser.add_option('-l', '--length', dest = "length", help = "Number of slots available", type = "int")
parser.add_option('-r', '--repeats', action="store_true", default=False, dest="repeats", help = "Whether colours repeat")

options, remainder = parser.parse_args()

colours = options.colours
length = options.length
repeats = options.repeats

if (options.length is None) or (options.colours is None):
    parser.print_help()
    sys.exit(1)

if colours < 1:
    print("At least one colour required.")
    sys.exit(2)

if length < 1:
    print("At least one slot required.")
    sys.exit(2)

if colours > len(COLOURS):
    print("Maximum number of colours is {}".format(len(COLOURS)))
    sys.exit(2)

if not repeats and (length > colours):
    print("Not enough colours ({}) to fill {} slots".format(colours, length))
    sys.exit(3)

def create_pool_with_repeats(colours, length):
    return list(map("".join, itertools.product(COLOURS[:colours], repeat=length)))

def create_pool_no_repeats(colours, length):
    return list(map("".join, itertools.permutations(COLOURS[:colours], length)))

def random_product(*args, repeat=4):
    "Random selection from itertools.product(*args, **kwds)"
    pools = [tuple(pool) for pool in args] * repeat
    return tuple(random.choice(pool) for pool in pools)

def random_permutation(iterable, r=None):
    "Random selection from itertools.permutations(iterable, r)"
    pool = tuple(iterable)
    r = len(pool) if r is None else r
    return tuple(random.sample(pool, r))

def random_guess(colours, length, repeats):
    if repeats:
        return random_product(COLOURS[:colours], repeat=length)
    else:
        return random_permutation(COLOURS[:colours], length)

def match(t1, t2):
    found = 0
    for i, v in enumerate(t1):
        if t2[i] == v:
            found += 1
    return found

def intersect(t1, t2):
    found = 0
    t2 = list(t2)
    for x in t1:
        if x in t2:
            t2.remove(x)
            found += 1
    return found

def verdict(guess, solution):
    black = match(guess, solution)
    white = intersect(guess, solution) - black
    return [black, white]

if repeats:
    pool = create_pool_with_repeats(colours, length)
    solution = random_product(COLOURS[:colours], repeat=length)
else:
    pool = create_pool_no_repeats(colours, length)
    solution = random_permutation(COLOURS[:colours], length)

guess = random_guess(colours, length, repeats)

print("Solution (with {}repeats):".format("" if repeats else "no "))
print(solution)
print("Total in pool: {}".format(len(pool)))

print("First guess: {}".format(guess))

print("Verdict: {}".format(verdict(guess, solution)))
