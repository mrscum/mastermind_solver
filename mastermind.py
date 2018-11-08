import itertools
import random
import optparse
import sys
import re
from collections import defaultdict

COLOURS = 'ABCDEFGHIJKLMNO'
MAX_TURNS = 12

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
    pools = [tuple(pool) for pool in args] * repeat
    return tuple(random.choice(pool) for pool in pools)

def random_permutation(iterable, r=None):
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

def verdict(turn, guess, solution):
    black = match(guess, solution)
    white = intersect(guess, solution) - black
    verdict = [black, white]

    verdict_history[turn] = verdict
    return verdict

def verdict_compare(turn_x, turn_y):
    verdict_comparison = {
        "black" : verdict_history[turn_y][0] - verdict_history[turn_x][0],
        "white" : verdict_history[turn_y][1] - verdict_history[turn_x][1],
        "count" : sum(verdict_history[turn_y]) - sum(verdict_history[turn_x])
    }
    return verdict_comparison

def assess_turn(guess, new_colour, verdict, verdict_compare, pool):
    pool.remove(''.join(guess))

    if verdict[0] == len(guess):
        print("You Win!")
        print("------------------------------------")
        sys.exit(0)

    # Rule 1
    for colour in guess:
        if colour in new_colour:
            for n, choice in enumerate(pool):
                if choice.count(colour) != verdict_compare['count']:
                    pool[n] = ''
    pool_count = pool.count('')
    print("Rule 1 choices removed: {}".format(pool_count))

    # Rule 2
    for i, choice in enumerate(pool):
        count = sum(1 for a, b in zip(''.join(guess), choice) if a != b)
        if count != (len(guess) - verdict[0]):
            pool[i] = ''
    pool_count = pool.count('') - pool_count
    print("Rule 2 choices removed: {}".format(pool_count))

    return list(filter(None, pool))

def attempt_guess(turn, new_colour, guess, solution, pool):
    result = verdict(turn, guess, solution)
    print("Verdict: {}".format(result))

    comparison = verdict_compare(turn-1, turn)
    new_pool = assess_turn(guess, new_colour, result, comparison, pool)
    print("Total in new pool: {}".format(len(new_pool)))

    if len(new_pool) == 0: 
        print("Error: No more solutions left in pool")
        sys.exit(1)

    new_pool.sort()
    return new_pool

if repeats:
    pool = create_pool_with_repeats(colours, length)
    solution = random_product(COLOURS[:colours], repeat=length)
else:
    pool = create_pool_no_repeats(colours, length)
    solution = random_permutation(COLOURS[:colours], length)

verdict_history = defaultdict(list)
verdict_history[0] = [0, 0]
turn = 1

# solution = ('E','G','E','D','C') 
# guess = ('E','C','B','A') 
# guess = random_guess(colours, length, repeats)
guess = tuple(pool[0])

print("Solution (with {}repeats):".format("" if repeats else "no "))
print(solution)
print("Total in pool: {}".format(len(pool)))
print("------------------------------------")
print("Turn {} guess: {}".format(turn, guess))
pool = attempt_guess(turn, COLOURS[turn-1], guess, solution, pool)
while turn < MAX_TURNS:
    turn+=1
    guess = tuple(pool[0])
    print("------------------------------------")
    print("Turn {} guess: {}".format(turn, guess))
    pool = attempt_guess(turn, COLOURS[turn-1], guess, solution, pool)
