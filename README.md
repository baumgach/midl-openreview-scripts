# MIDL Openreview Scripts

## About this repo

These are some quick and dirty Python scripts for interfacing with the Openreview platform, which I wrote for the [MIDL 2022 Conference](https://2022.midl.io/). The scripts are somewhat hacky and should mainly be used as templates for creating your own scripts for interfacing with the Openreview's Python API. 

## Requirements 

The code was most recently tested with Python 3.10.6 and the packages in the `requirements.txt` file. 

In order to run the scripts, you need to fill in your Openreview credentials in the call of `openreview.Client` of each script. 

You can install all requirements using 

````
pip install openreview-py pandas tqdm
````

or if you need to reproduce my exact environment use

````
pip install -r requirements.txt
````

Warning: There are two Openreview packages. The official one is `openreview-py` **not** `openreview`. 

## Description of the scripts

 * `make-paper-selection-table.py` creates a wide table with all review information for each paper. This can be formatted in Excel (or similar) to filter, and visualise in a way to make it useful for the final decision-making. 
 * `make-reviewer-rating-table.py` creates a table of all reviewer scores rated by the ACs. Useful for determining best reviewer awards. 
 * `make-gender-stats-table.py` collects all review, and meta-review scores along with first and last author gender as specified in the authors' Openreview profile. Useful for checking for potential biases in the review process. 