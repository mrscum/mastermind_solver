import itertools
import random

COLOURS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

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

pool_1 = create_pool_with_repeats(6, 4)
pool_2 = create_pool_no_repeats(8, 5)

print("Solution (with repeats):")
print(random_product('ABCDEF', repeat=4))
print("Total in pool 1: {}".format(len(pool_1)))
print("Solution (no repeats):")
print(random_permutation('ABCDEFGH', 5))
print("Total in pool 2: {}".format(len(pool_2)))

