# evolvinglife
An experiment with allowing Conway's Life to evolve from zero  
Requires: numpy, scikit-image, pygame

Start with a finite-but-infinitely-wrapping grid of cells. A cell can be either alive or dead, lit or dark, and irradiated or cold. A cell has eight neighboring cells, one in each cardinal and diagonal direction.  
All cells begin cold and dead. An initial pattern of lit and dark cells is specified.  
The following rules are then applied in order:
1. All cells become cold.
2. All cells with a lit neighbor to the right become lit. All others become dark.
3. Each cell becomes irradiated with some small probability, with lit cells having higher probability.
4. Cells that are irradiated and dead become alive, and cells that are irradiated and alive become dead.
5. Cells with three alive neighbors become alive, and cells with one or fewer alive neighbors, or four or more alive neighbors, become dead.
6. Go back to 1, repeat forever.

In essence, we're shining some sunlight on the world. Maybe, by chance, something will grow.  
On a large grid, over a long timespan, I would expect life to arise more frequently in brighter latitudes and to migrate toward darker ones.  
On a _very_ large grid, over a _very_ long timespan, that life may evolve to gain some resistance to radiation.

The script puts user-editable variables at the top, so users have a lot of fun knobs to tweak!
