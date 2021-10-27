Set of scripts and notebooks used to perform HGCAL trigger occupancy studies. Note that only occupancies in silicon modules are extracted.

# Default occupancies with constant threshold in the detector
## Production of occupancy files
The script `scripts/occupancy.py` will compute module occupancy values as well as word rate with various mipt thresholds. It takes as input a ROOT file containing a HGCAL TPG ntuple. 
Modules in different sectors and endcaps are wrapped onto a single sector. For this reason the rotated `u` and `v` of the modules need to be stored in the ntuple (`tv_waferurot` and `tc_wafervrot`), as well as the sector (`tc_sector`) and the endcap side (`tc_zside`).
The set of thresholds used to compute occupancy values is defined within the `occupancy.py` file. Thresholds are >0.5 mipT as this is the minimal value used in the ntuples.

The word rate is obtained converting numbers of TCs per modules into numbers of words, this mapping being stored in the file `data/ECON_TC_to_bits.csv`, the word rate is then computed as the mean value of the number of words.

The output is stored in a `csv` file containing the mean occupancy (`mean_occupancy`) and words (`mean_words`) indexed by the module identifier within a sector (`layer`, `waferu`, `waferv`) and the threshold (`threshold`). Additionally for each threshold, the full occupancy distributions are stored in several pickle files (one for each threshold).

## Plotting 
The occupancy plots are produced with the notebook `notebooks/data_occupancy.ipynb`. In order to plot occupancies in 1D it compute a mpdule `hash`, which is just the index in the list of modules sorted by `(layer, u, v)`. By matching module `hashes` it can compare occupancies obtained from different CMSSW versions. **Note that one has to be careful when comparing versions from geometries with different numbers of layers**. For this reason, when comparing the `D49` and `D86` geometries, the CE-H layers in `D86` are shifted by 2 in order to be matched with the CE-H layers in `D49`.

# Other studies
## Energy scale investigation
The notebook `notebooks/threshold_calibration.py` was used to investigate the energy scale of photons with the new electronics simulation, after issues were seen on occupancy values.

## Threshold tuning
Instead of computing the number of links needed for each module from occupancy values using a given threshold, the opposite can be done: computing the thresholds in each module given a number of links.
This has been studied with the other notebooks:
- `notebooks/compute_bit_rates.py`
- `notebooks/check_thresholdmap_occupancies.ipynb`
- `notebooks/produce_handmade_threshold_mappings.ipynb`
- `notebooks/proofofconcept_link_optimization.ipynb`


