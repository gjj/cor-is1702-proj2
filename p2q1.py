# G2_T11
# Goi Jia Jian, Nicolas Wijaya

# project 2 Q1

# replace the content of this function with your own algorithm
# inputs:
#   p: min target no. of points player must collect. p>0
#   v: 1 (non-cycle) or 2 (cycle)
#   flags: 2D list [[flagID, value, x, y], [flagID, value, x, y]....]
# returns:
#   1D list of flagIDs to represent a route. e.g. [F002, F005, F003, F009]
import copy

def get_route(p, v, flags):
    n = len(flags)

    f = {flags[i][0]: [float(flags[i][2]), float(
        flags[i][3]), int(flags[i][1])] for i in range(n)}
    f1 = copy.deepcopy(f)
    f2 = copy.deepcopy(f)

    # Part 1
    # Find out the paths of our two algorithms (same objective, but different measuring system)
    route1 = greedy(p, f1, f, 1)
    route2 = greedy(p, f2, f, 2)

    # Part 2
    # Improve each of the results above using the 2-opt method
    optimised1 = try2opt(route1, v, f)
    optimised2 = try2opt(route2, v, f)

    # Part 3
    # If best path from above gives more points than required,
    # check to see if by removing some points, whether it can be shorter
    result1 = trim(optimised1[1], p, v, f)
    result2 = trim(optimised2[1], p, v, f)

    # Part 4
    # Pick the best 2-opt optimised + trimmed route i.e. lowest distance of the above
    best_dist, best_route = min(result1, result2)
    
    return best_route

def greedy(p, f, flags, mode):
    points = 0
    current = [0, 0]
    result = []

    while p > points:
        local_best = {
            'flag': '',
            'weight_max': 0,
            'point': 0,
            'coord': [0, 0]
        }

        for id, [x, y, point] in f.items():
            if mode == 1:
                # mode = 1: Greedy search with objective max(point per unit distance travelled) method,
                # ignoring distance from SP, using Euclidean distance squared
                dist = get_distance_squared(current, [x, y])
                weight = point / dist

                if weight > local_best['weight_max']:
                    local_best['weight_max'] = weight
                    local_best['point'] = point
                    local_best['flag'] = id
                    local_best['coord'] = [x, y]

            elif mode == 2:
                # mode = 2: Greedy search with objective max(point per unit distance travelled) method,
                # ignoring distance from SP, using Euclidean distance
                dist = get_distance(current, [x, y])
                weight = point / dist

                if weight > local_best['weight_max']:
                    local_best['weight_max'] = weight
                    local_best['point'] = point
                    local_best['flag'] = id
                    local_best['coord'] = [x, y]

        result.append(local_best['flag'])
        del f[local_best['flag']]
        points += int(local_best['point'])
        current = local_best['coord']

    return result

def try2opt(route, v, flags):
    local_best = {
        'dist': get_route_dist(route, flags, v),
        'route': route
    }

    n = len(route)

    # 2-opt: Attempting to swap
    for i in range(0, n):
        for j in range(i+1, n):
            new_route = swap2opt(local_best['route'], i, j)
            new_dist = get_route_dist(new_route, flags, v)

            # If there exists a shorter path after the swap, keep the 2-opt swap
            # in hopes of searching for another best combination
            if new_dist < local_best['dist']:
                local_best['dist'] = new_dist
                local_best['route'] = new_route  # Copy the list

    return (local_best['dist'], local_best['route'])


def swap2opt(route, i, j):
    new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]  # left + right reversed + remaining
    return new_route

def trim(route, p, v, f):
    points = 0
    dist = get_route_dist(route, f, v) # Find distance of the best route

    # Find total points of this route
    for id in route:
        points += f[id][2]

    diff = points - p

    # Only run if diff > 0 i.e. the best route returns 502 points, but we only need 500
    if diff > 0:
        local_best = {
            'dist': dist,
            'route': route
        }

        # Prepare a sorted dict of points where it's equal to, or less than diff
        sorted_points = sorted({(f[id][2], id) for id in route if f[id][2] <= diff}, reverse=True)
        
        # For every (points, id) pair, check if after deleting it, will it give a lower distance?
        for to_delete in sorted_points:
            new_route = [item for item in route if item != to_delete[1]]
            new_dist = get_route_dist(new_route, f, v)

            # If it does give a lower distance, we keep it
            if new_dist < local_best['dist']:
                local_best['dist'] = new_dist
                local_best['route'] = new_route

        dist = local_best['dist']
        route = local_best['route']

    return (dist, route)

# Calculate Euclidean distance between two points e.g. (0, 0) and (-5.7, 8.8)
def get_distance(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

# Calculate Euclidean distance squared
def get_distance_squared(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

# Calculate total distance of a given path
def get_route_dist(your_route, flags_dict, v):
    dist = 0

    start_node = [0, 0]  # starting point SP (0, 0)
    last_node = start_node

    for flagID in your_route:
        curr_node = flags_dict[flagID]
        dist_to_curr_node = get_distance(last_node, curr_node)
        dist += dist_to_curr_node
        last_node = curr_node

    # If game mode v = 2, means have to cycle back to SP
    if v == 2:
        dist += get_distance(last_node, start_node)

    return dist