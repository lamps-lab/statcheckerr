from rpy2.robjects.packages import importr
utils = importr('utils')
utils.chooseCRANmirror(ind=1)
utils.install_packages("statcheck")
statcheck = importr("statcheck")
claim = "participants fixated the expected schematic cue earlier with increasing rape myth acceptance (RMA), leading to a negative correlation between RMA and total time (in ms) before the first fixation of the bottle of wine, r(24) = −.36, p < .05."
result = statcheck.statcheck(claim)
claims_error = 0
for row in result.iter_row():
  if (tuple(row[11])[0]):
    claims_error+=1
print("Number of errors in a claim: ", claims_error)
