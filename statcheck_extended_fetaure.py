from rpy2.robjects.packages import importr
utils = importr('utils')
utils.chooseCRANmirror(ind=1)
utils.install_packages("statcheck")
statcheck = importr("statcheck")

claim1 = "t(12)=4.3, p=0.01 and f(21,30)=2,3, p<0.02 and F(1,104) = 7.66, p=0.007; omega squared = 0.059."
# claim2 = "participants fixated the expected schematic cue earlier with increasing rape myth acceptance (RMA), \n leading to a negative correlation between RMA and total time (in ms) before the first fixation of the bottle of wine, r(24) = −.36, p < .05."
result = statcheck.statcheck(claim1)
claims_error = 0
count=0
threshold = 0
p_value = []
print("claim: ", claim1)
def p_value_sign(p_val):
  if(p_val == "<"):
    print("real_p_sign: -1")
  elif(p_val == "="):
    print("real_p_sign: 0")
  else:
    print("real_p_sign: 1")

def sample_size(stat,df_val,df1_val,):
  if(stat == "r"):
    if(df_val == "NA"):
      print("sample_size: ", df_val + 2 )
    else:
       print("sample_size: ", df1_val + 2 )
  elif(stat == "t"):
    if(df_val == "NA"):
      print("sample_size: ", df_val + 1 )
    else:
       print("sample_size: ", df1_val + 1 )
  elif(stat == "f" or stat == "F"):
    print("sample_size: ", df_val + df1_val+ 1 )


if (result):
  for row in result.iter_row():
    p_value.append(tuple(row[7])[0])
    count+=1
    if(tuple(row[7])[0]<=0.05):
      threshold+=1
    if (tuple(row[10])[0]):
     pass
    else:
       claims_error+=1
  p_value.sort()

  print("The real p-value: ", p_value[0])
  print("p-value range: ",p_value[count-1] - p_value[0] )
  for row in result.iter_row():
    if (tuple(row[7])[0] == p_value[0]):
      p_value_sign(tuple(row[6])[0])
      sample_size(tuple(row[1])[0], tuple(row[2])[0],tuple(row[3])[0])
      break


  print("Number of errors in a claim: ", claims_error)
  print("Number of p value expressions: ", count)
  print("Number of hypothesis tested: ", count)
  print("extend_p: ", 1)
  print("num_significant: ", threshold)
else:
  pass
