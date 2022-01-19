# statcheckerr

1. "statcheck.py" is the script to find statistical errors in claims
2. "statchek_extended_feature.py" is the script to find following features:     
    1. The real p-value
    2. p-value range
    3. real_p_sign
    4. sample_size
    5. Number of errors in a claim
    6. Number of p value expressions
    7. Number of hypothesis tested
    8. extend_p
    9. num_significant

# Description:

This repository contatins a script "statcheck.py" written in python. In this script, a package [rpy2] (https://rpy2.github.io/) was used to import "statcheck" to get the number of claims with statistical error and to enlist them.
# Requirements 
1. Python 3.7.12
2. rpy2
Following is the command to install rpy2 using pip:
    
    pip install rpy2

# Input and Output

Here is the sample input of two claims(claim 1 has statistical error and claim 2 is without error):
1. "participants fixated the expected schematic cue earlier with increasing rape myth acceptance (RMA), leading to a negative correlation between RMA and total time (in ms) before the first fixation of the bottle of wine, r(24) = −.36, p < .05, one-tailed."
2. "A 3 (response type) × 8 (lexical decision trial number) multilevel repeated-measures ANOVA on participants' transformed lexical decision latencies revealed a main effect of response type, F(2, 726) = 7.20,p < .001"

The output is - # of statistical errors in a claim
