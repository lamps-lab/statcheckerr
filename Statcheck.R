# claim_with_error = "participants fixated the expected schematic cue earlier with increasing rape myth acceptance (RMA), leading to a negative correlation between RMA and total time (in ms) before the first fixation of the bottle of wine, r(24) = −.36, p < .05, one-tailed."
# claim_without_error = "A 3 (response type) × 8 (lexical decision trial number) multilevel repeated-measures ANOVA on participants' transformed lexical decision latencies revealed a main effect of response type, F(2, 726) = 7.20,p < .001"

install.packages('plyr', repos = "http://cran.us.r-project.org")
library(statcheck)
cat("Please, enter a claim: ");
claim <- readLines("stdin",n=1);

claim_result = statcheck(claim)
claims_error = 0

if (!is.null(claim_result)){
    for (row in 1:nrow(claim_result)) {

        if (claim_result[row,'Error']==TRUE)
            {
                claims_error = claims_error + 1
                
            }
    }


}
if (claims_error > 0)
    {
        print("Number of errors in a claim")
        print(claims_error)
            
    }else
    {
       print("There is no error in the claim")
    }





