# featureExtractors.py
# --------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"Feature extractors for Pacman game states"

from game import Directions, Actions
import util

class FeatureExtractor:
    def getFeatures(self, state, action):
        """
          Returns a dict from features to counts
          Usually, the count will just be 1.0 for
          indicator functions.
        """
        util.raiseNotDefined()

class IdentityExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[(state,action)] = 1.0
        return feats

class CoordinateExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[state] = 1.0
        feats['x=%d' % state[0]] = 1.0
        feats['y=%d' % state[0]] = 1.0
        feats['action=%s' % action] = 1.0
        return feats

def getClosestIntersection(pos, walls):
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()    
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # check if there's an intersection at this location
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        if len(nbrs) > 3: #left, right, stop || up, down, stop
            return (dist, (int(pos_x), int(pos_y)))

        # otherwise spread out from the location to its neighbours
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))

    # no intersections found
    return None

def closestFood(pos, food, ghosts, walls):
    """
    closestFood -- this is similar to the function that we have
    worked on in the search project; here its all in one place
    """
    occupied = set()
    for ghost in ghosts:
        occupied.add((int(ghost[0]), int(ghost[1])))
    
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()    
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # if we find a food at this location then exit
        # check if there's a ghost at location too
        if food[pos_x][pos_y]:
            if (pos_x, pos_y) not in occupied:
                return dist
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))
    # no food found
    return None

def distanceToGhost(pos, ghost, walls):
    """
    closestFood -- this is similar to the function that we have
    worked on in the search project; here its all in one place
    """
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # if we find the ghost at this location then exit
        if (pos_x, pos_y) == (int(ghost[0]), int(ghost[1])):
            return dist
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))
    # no ghosts found
    return None

def distanceToGhosts(pos, ghosts, walls):
    result = []
    for ghost in ghosts:
        result.append(distanceToGhost(pos, ghost, walls))
    return result

def distanceToClosestGhost(pos, ghosts, walls):
    return min(distanceToGhosts(pos, ghosts, walls))

def closestCoords(pos, coords, walls):
    import operator
    # TODO: Cambiar distanceToGhosts a distanceToCoords
    dst = distanceToGhosts(pos, coords, walls)
    min_index, min_value = min(enumerate(dst), key=operator.itemgetter(1))
    return (int(coords[min_index][0]), int(coords[min_index][1]))

def isScared(state, ghost):
    return state.getGhostStateFromPosition(ghost).isScared()

class SimpleExtractor(FeatureExtractor):
    """
    Returns simple features for a basic reflex Pacman:
    - whether food will be eaten
    - how far away the next food is
    - whether a ghost collision is imminent
    - whether a ghost is one step away
    """
    
    # Detectar cuando se encuentre en un tunel: Dar la distancia a la salida mas cercana hacia donde se este mirando?
    # TODO: Si el entrenamiento da por debajo de 100 puntos en los primeros 10 episodios, reiniciar.

    def getFeatures(self, state, action):
        # extract the grid of food and wall locations and get the ghost locations
        food = state.getFood()
        walls = state.getWalls()
        ghosts = state.getGhostPositions()
        capsules = state.getCapsules()

        features = util.Counter()

        features["bias"] = 1.0

        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        # count the number of ghosts 1-step away
        features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts if not isScared(state, g))
        
        # calculate distances
        dist = closestFood((next_x, next_y), food, ghosts, walls)
        ghostsDists = distanceToGhosts((next_x, next_y), ghosts, walls)
        
        # if there is no danger of ghosts then add the food feature
        if (not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]) and (dist < min(ghostsDists) and food[next_x][next_y]):
            features["eats-food"] = 1.0

            # Distance to closest capsule
            #capsulesDists = distanceToGhosts((next_x, next_y), capsules, walls)
            #if len(capsulesDists) != 0:
            #    features["distance-to-closest-capsule"] = min(capsulesDists) / (walls.width * walls.height)

            # Distance to scared ghosts
            #for gi in range(len(ghostsDists)):
            #    if isScared(state, ghosts[gi]):
            #        features["distance-to-scared-ghost-"+str(gi+1)] = (float(ghostsDists[gi]) / (walls.width * walls.height))
        
        # Distance to ghosts
        #for gi in range(len(ghostsDists)):
        #    if not isScared(state, ghosts[gi]):
        #        features["distance-to-ghost-"+str(gi+1)] = (float(ghostsDists[gi]) / (walls.width * walls.height))

        # b(c): Distancia entre el fantasma mas cercano y la interseccion mas cercana (con respecto a ese fantasma)

        # Ghost danger
        # a = walls.width + walls.height
        # not_scared_ghosts = [g for g in ghosts if not isScared(state, g)]
        # if len(not_scared_ghosts) > 1:
        #     closestGhostCoords = closestCoords((next_x, next_y), ghosts, walls)
        #     closestIntersection = getClosestIntersection((next_x, next_y), walls)
        #     ghost2intersection = distanceToGhost(closestGhostCoords, closestIntersection[1], walls)
        #     features["ghost-danger"] = (a + closestIntersection[0] - ghost2intersection) / float(a)
            # features["ghost-danger"] =


        # Distance to closest food
        if dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            features["closest-food"] = float(dist) / (walls.width * walls.height)

        features.divideAll(10.0)
        return features
