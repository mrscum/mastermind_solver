import itertools
import random
import optparse
import sys
import re
from collections import defaultdict

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

    if verdict[0] == len(guess):    # [4, 0]
        print("You Win!")
        sys.exit(0)

    # Rule 1
    for colour in guess:            # remove solutions where new colour count doesn't match
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

    # Rule 3
    # elif sum(verdict) == 0:         # [0, 0]
    #     for colour in guess:
    #         for n, choice in enumerate(pool):
    #             if colour in choice:               
    #                 pool[n] = ''
    #     pool_count = pool.count('') - pool_count
    #     print("Rule 3 choices removed: {}".format(pool_count))

    # Rule 4
    # elif verdict[0] == sum(verdict) and verdict_compare['white'] < 0:           # [i, 0]
    #     template = ''.join(guess).replace(new_colour, ".")
    #     r = re.compile(template)
    #     newlist = list(filter(r.match, pool))
    #     for j, choice in enumerate(pool):   
    #         if pool[j] not in newlist:                
    #             pool[j] = ''
    #     pool_count = pool.count('') - pool_count
    #     print("Rule 4 choices removed: {}".format(pool_count))
        
        
    #     # for i, colour in enumerate(guess):
    #     #     if colour in new_colour:
    #     #         for j, choice in enumerate(pool):
    #     #             if pool[j] and guess[i] != choice[i]:  
    #     #             # if choice.count(colour) != verdict[0]:
    #     #                 # print("guess[i]: {}; choice[i]: {}".format(guess[i], choice[i]))
    #     #                 # print("removing: {}".format(choice))
    #     #                 pool[j] = ''
    #     # print(turn)

    # Rule 5
    # elif verdict[1] == sum(verdict):          # [0, i]
    #     for i, colour in enumerate(guess):      
    #         for j, choice in enumerate(pool):   
    #             if pool[j] and guess[i] == choice[i]:                
    #                 pool[j] = ''
    #     pool_count = pool.count('') - pool_count
    #     print("Rule 5 choices removed: {}".format(pool_count))

    # Rule 6
    # elif sum(verdict) == len(guess):        # [1, 3], [2, 2]
    #     pool = list(set(list(map("".join, itertools.permutations(guess, len(guess))))).intersection(pool))
    #     for i, choice in enumerate(pool):
    #         count = sum(1 for a, b in zip(''.join(guess), choice) if a != b)
    #         if verdict[1] != count:
    #             pool[i] = ''
    #     pool_count = pool.count('') - pool_count
    #     print("Rule 6 choices removed: {}".format(pool_count))

    # Rule 7
    # if verdict_compare['black'] < 0:            # If the number of blacks has decreased
    #     template = "." * len(guess)
    #     slots_with_colour = [i for i, colour in enumerate(guess) if colour == guess[0]]
    #     for i in slots_with_colour:
    #         template = template[:i] + guess[0] + template[i + 1:]
    #     r = re.compile(template)
    #     newlist = list(filter(r.match, pool))
    #     for j, choice in enumerate(pool):   
    #         if pool[j] in newlist:                
    #             pool[j] = ''
    #     pool_count = pool.count('') - pool_count
    #     print("Rule 7 choices removed: {}".format(pool_count))
    
    # if black, white == black, white from previous turn, then remove all solutions with the exact first x colours
    # where x is the sum of correct colours
    # if verdict_compare['black'] == 0 and verdict_compare['white'] == 0:
    #     template = "." * len(guess)
    #     i = 0
    #     while i < sum(verdict):
    #         template = template[:i] + guess[i] + template[i + 1:]
    #         i += 1
    #     # print("template: {}".format(template))
    #     r = re.compile(template)
    #     newlist = list(filter(r.match, pool))
    #     # print("New List: {}".format(newlist))
    #     for j, choice in enumerate(pool):   
    #         if pool[j] in newlist:                
    #             pool[j] = ''

    # If sum remains the same, there are still 1+ white and sum != len(guess) 
    # then make a template from the correct colours and remove their exact position from possible solutions
    
    # Rule 8
    # if verdict_compare['count'] == 0 and sum(verdict) != len(guess) and verdict[1] > 0:
    #     template = ''.join(guess).replace(new_colour, ".")
    #     r = re.compile(template)
    #     newlist = list(filter(r.match, pool))
    #     for j, choice in enumerate(pool):   
    #         if pool[j] in newlist:                
    #             pool[j] = ''
    #     pool_count = pool.count('') - pool_count
    #     print("Rule 8 choices removed: {}".format(pool_count))

    # else: 
    #     print("Don't know what to do next...")
    #     print("Total remaining in pool: {}".format(sum(x is not '' for x in pool)))
    #     sys.exit(1)

    return list(filter(None, pool))

def attempt_guess(turn, new_colour, guess, solution, pool):
    # print("Turn {} guess: {}".format(turn, guess))

    result = verdict(turn, guess, solution)
    print("Verdict: {}".format(result))

    print(verdict_history.items())
    comparison = verdict_compare(turn-1, turn)
    print("Verdict comparison: {}".format(comparison))

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

# solution = ('D','F','D','D') 
# guess = ('E','C','B','A') 
# guess = random_guess(colours, length, repeats)
guess = tuple(pool[0])

print("Solution (with {}repeats):".format("" if repeats else "no "))
print(solution)
print("Total in pool: {}".format(len(pool)))

print("Turn {} guess: {}".format(turn, guess))
pool = attempt_guess(turn, COLOURS[turn-1], guess, solution, pool)
while turn < 10:
    turn+=1
    guess = tuple(pool[0])
    print("Turn {} guess: {}".format(turn, guess))
    pool = attempt_guess(turn, COLOURS[turn-1], guess, solution, pool)
