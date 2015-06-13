#!/bin/bash
python pacman.py -p ApproximateQAgent -a extractor=SimpleExtractor -l mediumClassic --ghosts DirectionalGhost --numghosts 2 -x 10 -n 1010  --frameTime -1
