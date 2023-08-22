#!/usr/bin/python3

# evolvinglife.py: An experiment with allowing Conway's Life to evolve from zero, by Bradley Allen
# Version 1.0 - it's slow, but it works!
# Requires: numpy, scikit-image, pygame

# Start with a finite-but-infinitely-wrapping grid of cells. A cell can be either alive or dead, lit or dark, and irradiated or cold. A cell has eight neighboring cells, one in each cardinal and diagonal direction.
# All cells begin cold and dead. An initial pattern of lit and dark cells is specified.
# The following rules are then applied in order:
# 1. All cells become cold.
# 2. All cells with a lit neighbor to the right become lit. All others become dark.
# 3. Each cell becomes irradiated with some small probability, with lit cells having higher probability.
# 4. Cells that are irradiated and dead become alive, and cells that are irradiated and alive become dead.
# 5. Cells with three alive neighbors become alive, and cells with one or fewer alive neighbors, or four or more alive neighbors, become dead.
# 6. Go back to 1, repeat forever.

# In essence, we're shining some sunlight on the world. Maybe, by chance, something will grow.
# On a large grid, over a long timespan, I would expect life to arise more frequently in brighter latitudes and to migrate toward darker ones.
# On a very large grid, over a very long timespan, that life may evolve to gain some resistance to radiation. (TODO improve efficiency and speed to enable testing this)

# Thanks to Ingo Berg for some implementation ideas, https://beltoforion.de/en/recreational_mathematics/game_of_life.php
# Any blatant stupidities should be assumed to be my own.

# This code is tab-indented, please set your editor appropriately. This doesn't count as one of the stupidities.

#########
#
# LOTS OF FUN KNOBS TO TWEAK
#
#########

# Grid size, measured in cells.
GRID_SIZE_X = 200
GRID_SIZE_Y = 100

# Each cell is a square, drawn with this many pixels per side.
CELL_SIZE = 5

# Set whether the grid is windowed or fullscreen. If fullscreen, set the grid size and cell size above to match your display.
FULLSCREEN = False

# Additional time to wait between turns/generations, specified in seconds. Set to 0 to run at maximum speed.
TIME_DELAY = 0

# Setting good radiation values is key. Too low, and nothing will grow for a long time (if ever). Too high, and things will rapidly get out of hand.
# For larger grids, use lower values. Impatient gods should use higher ones.
SOLAR_RADIATION = 0.005
COSMIC_RADIATION = 0.00005

# Conway's Game of Life uses the B3/S23 rule, but you can change it here.
LIFE_BIRTH_STATES = [3]
LIFE_SURVIVAL_STATES = [2,3]

# Colors are indexed by cell value. So a cell that has value 0 (dark, cold, and dead) will use COLORS[0], and a cell with value 7 (lit, irradiated, and alive) will use COLORS[7].
COLORS = [
	(0, 0, 0),
	(127, 0, 0),
	(0, 0, 127),
	(127, 0, 127),
	(0, 255, 0),
	(127, 255, 0),
	(0, 255, 127),
	(127, 255, 127)]

#########
#
# END OF FUN KNOBS TO TWEAK
#
#########

import numpy as np
from skimage.draw import ellipse
import pygame
import time

CONST_LIT = 1
CONST_IRRADIATED = 2
CONST_ALIVE = 4
MASK_DARK = CONST_IRRADIATED | CONST_ALIVE
MASK_COLD = CONST_LIT | CONST_ALIVE
MASK_DEAD = CONST_LIT | CONST_IRRADIATED

def main():
	pygame.init()
	if FULLSCREEN:
		surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
	else:
		surface = pygame.display.set_mode((GRID_SIZE_X * CELL_SIZE, GRID_SIZE_Y * CELL_SIZE))
	generation = 0
	grid = init_grid()
	surface.fill(COLORS[0])
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				return
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					return
		pygame.display.set_caption("Evolving Life (Generation: " + str(generation) + ")")
		draw(grid, surface)
		time.sleep(TIME_DELAY)
		grid = next_step(grid)
		generation += 1

def init_grid():
	# build an empty grid, then drop an ellipse of light on it. 
	grid = np.zeros((GRID_SIZE_Y, GRID_SIZE_X), dtype=int)
	pattern_size_x = int(GRID_SIZE_X / 2)
	pattern_size_y = GRID_SIZE_Y
	pattern = np.zeros((pattern_size_y, pattern_size_x), dtype=int)
	rr, cc = ellipse(pattern_size_y/2, pattern_size_x/2, pattern_size_y/2, pattern_size_x/2)	# from skimage
	pattern[rr, cc] = 1
	grid[0:pattern_size_y, pattern_size_x:GRID_SIZE_X] = pattern
	return grid

def next_step(grid):
	# make all cells cold
	grid &= MASK_COLD
	# move sun, irradiate, and apply effects of radiation 
	rng = np.random.default_rng()
	new_grid = grid.copy()
	for j in range(GRID_SIZE_Y):
		for i in range(GRID_SIZE_X):
			# move sun
			if is_lit(grid, (i+1)%GRID_SIZE_X, j):
				new_grid[j,i] |= CONST_LIT
			else:
				new_grid[j,i] &= MASK_DARK
			# irradiate
			if is_lit(new_grid, i, j):
				if rng.random() <= (COSMIC_RADIATION + SOLAR_RADIATION): new_grid[j,i] |= CONST_IRRADIATED
			else:
				if rng.random() <= COSMIC_RADIATION: new_grid[j,i] |= CONST_IRRADIATED
			# effects of radiation
			if is_irradiated(new_grid, i, j):
				new_grid[j,i] ^= CONST_ALIVE
	# life rules
	new_new_grid = new_grid.copy()	# object assignments are done by-ref in Python, leading to a NaiveLife implementation unless you specifically call copy(). it took me a bit to track that one down.
	for j in range(GRID_SIZE_Y):
		for i in range(GRID_SIZE_X):
			neighborhood = count_alive_neighbors(new_grid, i, j)
			if neighborhood in LIFE_BIRTH_STATES:
				new_new_grid[j,i] |= CONST_ALIVE
			elif neighborhood not in LIFE_SURVIVAL_STATES:
				new_new_grid[j,i] &= MASK_DEAD
	return new_new_grid

def count_alive_neighbors(grid, x, y):
	alive_count = 0
	# check the eight surrounding tiles
	if is_alive(grid, x, (y-1)%GRID_SIZE_Y): alive_count += 1	# N
	if is_alive(grid, (x+1)%GRID_SIZE_X, (y-1)%GRID_SIZE_Y): alive_count += 1	# NE
	if is_alive(grid, (x+1)%GRID_SIZE_X, y): alive_count += 1	# E
	if is_alive(grid, (x+1)%GRID_SIZE_X, (y+1)%GRID_SIZE_Y): alive_count += 1	# SE
	if is_alive(grid, x, (y+1)%GRID_SIZE_Y): alive_count += 1	# S
	if is_alive(grid, (x-1)%GRID_SIZE_X, (y+1)%GRID_SIZE_Y): alive_count += 1	# SW
	if is_alive(grid, (x-1)%GRID_SIZE_X, y): alive_count += 1	# W
	if is_alive(grid, (x-1)%GRID_SIZE_X, (y-1)%GRID_SIZE_Y): alive_count += 1	# NW
	return alive_count

def draw(grid, surface):
	# draw each square of the current grid
	for j in range(GRID_SIZE_Y):
		for i in range(GRID_SIZE_X):
			pygame.draw.rect(surface, COLORS[grid[j][i]], (i*CELL_SIZE, j*CELL_SIZE, CELL_SIZE, CELL_SIZE))
	pygame.display.update()

def is_lit(grid, x, y):
	return bool(grid[y,x] & CONST_LIT)

def is_irradiated(grid, x, y):
	return bool(grid[y,x] & CONST_IRRADIATED)

def is_alive(grid, x, y):
	return bool(grid[y,x] & CONST_ALIVE)

if __name__ == '__main__':
    main()
