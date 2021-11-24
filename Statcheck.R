install.packages('plyr', repos = "http://cran.us.r-project.org")
library(statcheck)

dataset <- read.csv(file = THIS_IS_YOUR_CSV_FILE)
claims = dataset[, c(THIS_IS_YOUR_CSV_FILE_Column_Name)]


claims_error = 0
claims_list = list()
counter = 1

for (claim in claims) {
    
    print("---------------------------------")
    result = statcheck(claim)
    
    if (!is.null(result)){
        if (result['Error']==TRUE)
        {
            claims_error = claims_error+1
            claims_list <- c(claims_list, claim)
            
            

     
        }

    }
    counter1 = counter1 + 1

}



print("-----------Number of Error in claims-------------")

print(claims_error)

print("-------------Claim List with error-------------")

print(claims_list)