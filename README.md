# statcheckerr

Script to find statistical errors in claims.

# Description:

This repository contatins a script "Statcheck.R" written in R programming language. In this script, a R package [statcheck] (https://rpubs.com/michelenuijten/statcheckmanual) was used to get the number of claims with statistical error and to enlist them.

To run the script, the following command can be executed:

    Rscript Statcheck.R

# Input and Output

If you run the script, it will ask for an user input of a claim. Here is the example of two claims(claim 1 has statistical error and claim 2 is without error):
1. "participants fixated the expected schematic cue earlier with increasing rape myth acceptance (RMA), leading to a negative correlation between RMA and total time (in ms) before the first fixation of the bottle of wine, r(24) = −.36, p < .05, one-tailed."
2. "A 3 (response type) × 8 (lexical decision trial number) multilevel repeated-measures ANOVA on participants' transformed lexical decision latencies revealed a main effect of response type, F(2, 726) = 7.20,p < .001"

The output is - # of statistical error in a claim
