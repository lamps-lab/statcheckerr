# statcheckerr

Script to find statistical errors in claims.

# Description:

This repository contatins a script "Statcheck.R" written in R programming language. In this script, a R package [statcheck] (https://rpubs.com/michelenuijten/statcheckmanual) was used to get the number of claims with statistical error and to enlist them.

To run the script, the following command can be executed:

    Rscript Statcheck.R

# Input and Output

* For this script, the input will be a CSV file that contains the claims. 
* In the script, in line 4, replace the string "THIS_IS_YOUR_CSV_FILE" with your CSV file name.
* In line 5, replace the string "THIS_IS_YOUR_CSV_FILE_Column_Name" by the column name that contains 
the claims.
* The output of this script is - # of claims with statistical error and the list of the claims with statistical 
error.
