# Cosmic Ray Remover
General purpose cosmic ray removal tool

### Requirements
```
numpy
PIL
scipy
skimage
```

## CLI Usage

`run_CR.py` will iteratively find and reduce pixel values of features that have been determined to be due to cosmic rays. See the following paper for details:

"Cosmic-Ray Rejection by Laplacian Edge Detection"
Pieter G. van Dokkum
Astronomical Society of the Pacific, 113:1420–1427, 2001

https://doi.org/10.1086/323894

### Minimal usage

```
python3 run_CR.py -img IMAGENAME
```

This will process the image "IMAGENAME" using the default values, i.e.:
```
S = 2 
LF = 5
mode = 'both' # Satisfies both S and LF thresholds
```

`read_noise = 12.38`, `gain = 1.00`, and `subsamp_fac = 2` are currently hardcoded for `run_CR.py` but are parameters within `CosmicRemove.py`.
