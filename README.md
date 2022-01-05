# statcheckerr

Script to find statistical errors in claims.

# Description:

This repository contatins a script "statcheck.py" written in python. In this script, a package [rpy2] (https://rpy2.github.io/) was used to get the number of claims with statistical error and to enlist them.
# Requirements 

Following is the command to install rpy2 using pip:
    
    pip install rpy2

# Input and Output

Here is the sample input of two claims(claim 1 has statistical error and claim 2 is without error):
1. "participants fixated the expected schematic cue earlier with increasing rape myth acceptance (RMA), leading to a negative correlation between RMA and total time (in ms) before the first fixation of the bottle of wine, r(24) = −.36, p < .05, one-tailed."
2. "A 3 (response type) × 8 (lexical decision trial number) multilevel repeated-measures ANOVA on participants' transformed lexical decision latencies revealed a main effect of response type, F(2, 726) = 7.20,p < .001"

The output is - # of statistical errors in a claim
