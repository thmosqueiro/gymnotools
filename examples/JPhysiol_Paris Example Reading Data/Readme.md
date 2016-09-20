JPhysiol_Paris Example Reading Data
====



<img src="" style="width: 80%; float: left; margin: 0 0 10px 10px;" />



Download the dataset
---

The dataset is publicly available at [FigShare]() (URL will be
provided shortly), and contains 3 different recordings from 11
different channels. The compressed size of the dataset is _4.66 GB_.


Relevant papers
---

If you find this useful, please star this repository and/or cite our paper:

* RT Guariento, T Mosqueiro, P Matias, VB Cesarino, LOB Almeida, JFW
  Slaets, LP Maia & RD Pinto, [Automated pulse discrimination of two
  freely-swimming weakly electric fish and analysis of their
  electrical behavior during a dominance
  contest](https://www.researchgate.net/publication/304787186_Automated_pulse_discrimination_of_two_freely-swimming_weakly_electric_fish_and_analysis_of_their_electrical_behavior_during_a_dominance_contest)
  (Under review).

* T Mosqueiro, M Strube-Bloss, RT Guariento, RD Pinto, B Smith & R
  Huerta, [Non-parametric Change Point Detection for Spike
  Trains](https://www.researchgate.net/publication/292982370_Non-parametric_Change_Point_Detection_for_Spike_Trains?ev=prf_pub). Talk
  presented on Information Sciences and Systems (CISS), Princeton
  2016.


Directions in Linux systems
---

To get started, simply download the dataset and put the files in a
folder. You can unzip these files by simply typing the following
command:
```
unzip Guariento*.zip
```
Notice that we are assuming that there are no other zipped files with
names that start with "Guariento". In a common laptop, this may take
several minutes (up to 5 minutes in a Intel i5 processor). After all
files are unzipped, you should see three new files with extension
_memampf32_. These are the files containing the recordings from the
large aquarium.

In the present repository, we are providing a sample python script
that reads and plots the first 300ms of these files. This script is
called _plot_example.py_, and can be executed by simply typing the
following:
```
python plot_example.py
```
It should not take longer than a few seconds, and a file named
_"Example of Plot.png"_ should be created with the plot. The quality
of the png can be improved by increasing the dpi parameter at the end
of _plot_example.py_.

In the following, we present a minimal example to simply read our
recordings.
```
import numpy as np
V = np.memmap("15o04000.abf.memampf32", dtype=np.float32)
```
This will store in variable V the time series from all channels
recorded during our experiment. To access a particular channel, say,
7, you can use:
```
Ch7 = X[7::11]
```



Dependencies
---

* Dataset, which is available at FigShare (see above)

* Python 2.*

* numpy 11.*+

* matplotlib 1.10+