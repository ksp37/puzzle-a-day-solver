# Puzzle a Day Solver

## Overview

This is a solver for Dragon Fjord’s [Puzzle a Day](https://www.dragonfjord.com/). It was a personal challenge I set myself, so the code is very much *rough and ready* (as is evident from the naming and messy implementation!).

The main challenge was writing the algorithm (`solver.py`), and no AI was used for this part. I did, however, use AI to code a visualisation of the solution, contained entirely within `visualisation.py`.

## Generating Shape Possibilities

The basic approach is a brute-force search, although this isn't as trivial as it sounds. Each piece needs to be tried in every position and orientation, and can also be flipped. I coded this systematically to ensure I covered all possibilities for each shape, but in doing so, I introduced duplicates.

It might have been possible to avoid generating duplicates in the first place, but I instead took the approach of removing them once all possibilities had been calculated.

The standard approach would be to sort the coordinates for each shape and then compare them. Instead, I decided to map each coordinate to a prime number and use (1) the commutativity of multiplication and (2) the unique factorisation guaranteed by the fundamental theorem of arithmetic to generate a hash for each possibility.

Why this approach? Honestly, I forgot about sorting at the time, but it's also nice, from a purity perspective, that it doesn't rely on an external sorting algorithm.

## Solving the Puzzle: Dancing Links

With all shape possibilities generated, the next step is to combine them to create coverings of the board. Most of these will be partial coverings, since it's actually quite hard to fit all the pieces on the board.

From my own experience, there didn't seem to be a human heuristic to try to emulate in the solver. However, a bit of good old-fashioned Googling led me to the exact cover problem and Donald Knuth's Dancing Links technique.

This was the first I'd heard of it, and it seemed like a really cool, efficient way to search: by prioritising the constraint with the fewest remaining possibilities. It also felt like a good stretch goal to try to implement the algorithm from scratch, using just the description on Wikipedia.

That explains why my version is quite ugly!

## Constructing the Exact Cover Matrix

One of the hardest parts — and the bit where I was on my own — was setting up the matrix used by the algorithm. This is specific to each covering problem, so some thought is needed to represent the problem correctly.

The Puzzle a Day board is not a genuine 7 × 7 grid, because some cells are unavailable. The date you're trying to solve also makes two additional cells unavailable.

The matrix columns represent grid cells, and each row represents a possible placement of a shape. The unavailable cells must also be accounted for, so a row representing the condition that those cells cannot be occupied by a shape must be included in the solution.

Converting each shape possibility into a row is straightforward enough. The tricky bit is that this is a sparse matrix, with each non-zero element represented by a node. Each node must be linked to its neighbours in the same row and column, and some additional bookkeeping is necessary for DLX (hence the header node).

## Implementation Notes

There are a few redundancies and inefficiencies in my algorithm, but nothing that, I hope, significantly affects the runtime.