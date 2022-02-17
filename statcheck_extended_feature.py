import re
import spacy
import os
from spacy.lang.en import English
from collections import namedtuple
import pandas as pd
import csv
import re
import string

nlp = spacy.load("en_core_web_sm")
# Load English tokenizer, tagger, parser, NER and word vectors
nlp = English()

# Create the pipeline 'sentencizer' component
sbd = nlp.create_pipe('sentencizer')

# Add the component to the pipeline
nlp.add_pipe(sbd)

# Max length for input (Memory bottleneck)
nlp.max_length = 6000000

#get p-values if any in given claims csv---------------------------------------------------------------------------------
def get_p_val_darpa_tsv(claim):
    pattern_p = re.search("(p|P|Ps|ps)\s*(<|>|=)\s*-?\d*\.*\d+(e(-|–)\d+)?", claim)
    if pattern_p:
        return pattern_p.group()
    else:
        return None


p_val_sign = {
    '<': -1,
    '=': 0,
    '>': 1
}


def remove_accents(text: str):
    text = re.sub('[âàäáãå]', 'a', text)
    text = re.sub('[êèëé]', 'e', text)
    text = re.sub('[îìïí]', 'i', text)
    text = re.sub('[ôòöóõø]', 'o', text)
    text = re.sub('[ûùüú]', 'u', text)
    text = re.sub('[ç]', 'c', text)
    text = re.sub('[ñ]', 'n', text)
    text = re.sub('[ÂÀÄÁÃ]', 'A', text)
    text = re.sub('[ÊÈËÉ]', 'E', text)
    text = re.sub('[ÎÌÏÍ]', 'I', text)
    text = re.sub('[ÔÒÖÓÕØ]', 'O', text)
    text = re.sub('[ÛÙÜÚ]', 'U', text)
    text = re.sub('[Ç]', 'C', text)
    text = re.sub('[Ñ]', 'N', text)
    return text


def strip_punctuation(text: str):
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    text = re.sub(regex, "", text)
    text = text.strip()
    return text


def read_darpa_tsv(file):
    df = pd.read_csv(file, sep="\t")
    for index, row in df.iterrows():
        try:
            yield {"title": row['title_CR'], "pub_year": row['pub_year_CR'], "doi": row['DOI_CR'],
               "ta3_pid": row['ta3_pid'], "pdf_filename": row['pdf_filename'], "claim4": row['claim4_inftest']}
        except KeyError:
            ta3_pid = row['pdf_filename'].split()[-1]
            yield {"title": row['title_CR'], "pub_year": row['pub_year_CR'], "doi": row['DOI_CR'],
                   "ta3_pid": ta3_pid, "pdf_filename": row['pdf_filename'], "claim4": row['claim4_inftest']}


def elem_to_text(elem, default=''):
    if elem:
        return elem.getText()
    else:
        return default


# Return CSV writer object
def csv_writer(filename, append=False):
    if append:
        writer = csv.writer(open(filename, 'a', newline='', encoding='utf-8'))
    else:
        writer = csv.writer(open(filename, 'w', newline='', encoding='utf-8'))
    return writer


# Write header into CSV
def csv_write_field_header(writer, header):
    writer.writerow(header)


# Write dict based record into CSV in order
def csv_write_record(writer, record, header):
    nt_record = namedtuple('dis_features', header)
    sim_record = nt_record(**record)
    writer.writerow(list(sim_record))


#function for extraction of p-values and sample sizes from text files------------------------THIS IS THE MAIN FUNCTION--------------------------------------------------
def extract_p_values(text, tsv_claim=None):
    p_val_list = []
    sample_list = []
    real_sample_list = []
    intext_samplesize = []
    filtered_sent = []
    sentences = []
    just_pvalues_list = []
    just_pvalues_range = []
    max_sample_size = 0
    range_p_values = 0
    real_p_sign = 0
    num_hypo_test = 0
    real_p_value = 1
    number_significant = 0
    extended_p_val = 0

    try:
        # text = open(file, "r", encoding="utf8")
        # text = open(file, "r")
        text1 = text
    except FileNotFoundError:
        print("******---------- File not found: ", file, "----------******")
        return {"num_hypo_tested": num_hypo_test, "real_p": real_p_value, "real_p_sign": real_p_sign,
                "p_val_range": range_p_values, "num_significant": number_significant, "sample_size": max_sample_size,
                "extend_p": extended_p_val}
    except UnicodeDecodeError:
        try:
            text = open(file, "r", encoding="utf-8")
            text1 = text.read()
        except UnicodeDecodeError:
            print("*********---------- Encoding error: ", file, "*********----------")
            return {"num_hypo_tested": num_hypo_test, "real_p": real_p_value, "real_p_sign": real_p_sign,
                    "p_val_range": range_p_values, "num_significant": number_significant,
                    "sample_size": max_sample_size, "extend_p": extended_p_val}

    #  "nlp" Object is used to create documents with linguistic annotations.
    doc = nlp(text1)
    # create list of sentence tokens
    for word in doc:
        if not word.is_stop:
            filtered_sent.append(word)

    for sent in doc.sents:
        sentences.append(sent.text)

    for i in range(0, len(sentences) - 1):

        #********REGEX FOR PA FORMATTED DISTRIBUTIONS******************

        #expression for t test statistic and p-value
        pattern_t_list = re.finditer("t\\s?(\[|\()\\s?\\d*\\.?\\d+\\s?(\]|\))\\s?[<>=]\\s?[^a-z\\d]{0,3}\\s?\\d*[,;]?\\d*\\.?\\d+\\s?[,;]\\s?(([^a-z]ns)|([p|P]\\s?[<>=-]\\s?\\d?\\.\\d+e?(-|–)?\\d*))", sentences[i])
        pattern_t_nodf_list = re.finditer("t\\s?([<>=]|\\s?)\\s?[^a-z\\d]{0,3}\\s?\\d*[,;]?\\d*\\.?\\d+\\s?[,;]\\s?(([^a-z]ns)|([p|P]\\s?[<>=-]\\s?\\d?\\.\\d+e?-?\\d*))", sentences[i])

        #expression for f test statistic and p-value
        pattern_f_list = re.finditer("(F|F-change)\\s?(\[|\()\\s?\\d*\\.?(I|l|\\d+)\\s?,\\s?\\d*\\.?\\d+\\s?(\]|\))\\s?[<>=]\\s?\\d*\\.?\\d+\\s?[,;]\\s?(([^a-z]ns)|([p|P]\\s?[<>=-]\\s?\\d?\\.\\d+e?(-|–)?\\d*))", sentences[i])
        # pattern_f_list = re.finditer("F\s*(\[|\()\s*\d*\.*(I|l|\d+)\s*,\s*\d*\.*\d+\s*(\]|\))\s*[<>=]\s*\d*\.?\d+\s*[,;]\s*(([^a-z]ns)|([p|P]\s*[<>=-]\s*\d*\.\d+e*-*\d*))", sentences[i])
        
        #expression for correlation r vs p-value
        pattern_cor_list = re.finditer("r\\s?\\(\\s?\\d*\\.?\\d+\\s?\\)\\s?[<>=]\\s?[^a-z\\d]{0,5}\\s?\\d*\\.?\\d+\\s?[,;]\\s?(([^a-z]ns)|([p|P]\\s?[<>=-]\\s?\\d?\\.\\d+e?(-|–)?\\d*))", sentences[i])
        pattern_cor_no_df_list = re.finditer("(r|rpb|R)\s*\s*[<>=]\s*[^a-z\d*]{0,5}\s*\d*\.?\d+\s*[,;]\s*(([^a-z]ns)|([p|P]\s*[<>=-]\s*\d*\.\d+e?(-|–)?\d*))", sentences[i])

        # expression for z test statistic and p-value
        pattern_z_list = re.finditer("[^a-z]z\\s?[<>=]\\s?[^a-z\\d]{0,3}\\s?\\d*,?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|([p|P]\\s?[<>=-]\\s?\\d?\\.\\d+e?(-|–)?\\d*))", sentences[i])

        #expression for chi square test statistic vs p-value
        pattern_chi_list = re.finditer("((\\[CHI\\]|\\[DELTA\\]G)\\s?|(\\s[^trFzQWBn ]\\s?)|([^trFzQWBn ]2\\s?))2?\\(\\s?\\d*\\.?\\d+\\s?(,\\s?N\\s?\\=\\s?\\d*\\,?\\d*\\,?\\d+\\s?)?\\)\\s?[<>=]\\s?\\s?\\d*,?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|([p|P]\\s?[<>=]\\s?\\d?\\.\\d+e?(-|–)?\\d*))", sentences[i])

        #expression for q test statistic vs p-value
        pattern_q_list = re.finditer("Q\\s?-?\\s?(w|within|b|between)?\\s?\\(\\s?\\d*\\.?\\d+\\s?\\)\\s?[<>=]\\s?[^a-z\\d]{0,3}\\s?\\d*,?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|([p|P]\\s?[<>=]\\s?\\d?\\.\\d+e?(-|–)?\\d*))", sentences[i])

        #expression for logistic regression test statistic and p-value
        pattern_logreg_list = re.finditer("[OR|or|oR|Or]\\s?\\s?[<>=]\\s?[^a-z\\d]{0,5}\\s?\\d*\\.?\\d+\\s?[,;]\\s?(([^a-z]ns)|([p|P]\\s?[<>=-]\\s?\\d?\\.\\d+e?-?\\d*))", sentences[i])

        #expression for Hazard Ratio test statistic and p-value
        pattern_HR_list = re.finditer("HR[\s*|=]\d*\.*\d*,\s*(.*,(.*[p|P]\s*[<>=]\s*\d*\.\d+e?[-|–]*\d*))", sentences[i])

        #expression for b test statistic (unstandardalized beta)
        pattern_b_list = re.finditer("b\s*[=><]\s*\d*\.*\d*\s*,\s*[p|P]\s*[<>=]\s*\d*\.\d+e*[-|–]*\d*", sentences[i])

        #expression for d distribution (possion ratio related)
        pattern_d_list = re.finditer("d\s*[=><]\s*\d*\.*\d*\s*,\s*[p|P]\s*[<>=]\s*\d*\.\d+e*[-|–]*\d*", sentences[i])


        #*****************REGEX FOR P VALUE EXPRESSION FROM DISTRIBUTION*****************************
        pattern_p = re.search( "(p|P|Ps|ps)\s*(<|>|=)\s*-?\d*\.*\d+(e(-|–)\d+)?", sentences[i])


        # --------------------------------------T-DISTRIBUTION---------------------------------------------

        for pattern_t in pattern_t_list:
            if pattern_t:
                expression = pattern_t.group()
                # print(expression)
                pattern_pval = re.search( "(p|P|Ps|ps)\s*(<|>|=)\s*-?\d*\.*\d+(e(-|–)\d+)?", expression)
                if pattern_pval:
                    reported_pval_exp = pattern_pval.group()
                    p_val_list.append(reported_pval_exp)
                
                s = [float(s) for s in re.findall(r'-?\d+\.?\d*', expression)]
                if len(s) == 3:
                    df2 = 'NULL'
                    df1 = s[0]
                    sample_t = df1 + 1
                    sample_list.append(sample_t)

                else:
                    df2 = s[1]
                    df1 = s[0]
                    sample_t = df1 + 1
                    sample_list.append(sample_t)

        for pattern_t_nodf in pattern_t_nodf_list:
            if pattern_t_nodf:
                expression = pattern_t_nodf.group()
                # print(expression)
                pattern_pval = re.search( "(p|P|Ps|ps)\s*(<|>|=)\s*-?\d*\.*\d+(e(-|–)\d+)?", expression)
                # print(pattern_pval)
                if pattern_pval:
                    reported_pval_exp = pattern_pval.group()
                    p_val_list.append(reported_pval_exp)
                   

        # --------------------------------------------------F-DISTRIBUTION--------------------------------

        for pattern_f in pattern_f_list:
            if pattern_f:
                expression = pattern_f.group()
                pattern_pval = re.search( "(p|P|Ps|ps)\s*(<|>|=)\s*-?\d*\.*\d+(e(-|–)\d+)?", expression)
#                 print(pattern_pval)
                if pattern_pval:
                    reported_pval_exp = pattern_pval.group()
                    p_val_list.append(reported_pval_exp)
                    s = [float(s) for s in re.findall(r'-?\d+\.?\d*', expression)]
                    if len(s) == 3:
                        df2 = s[1]
                        df1 = s[0]
                        constant = df1 + 1
                        sample_f = constant + df2
                        sample_list.append(sample_f)

                    else:
                        df2 = s[1]
                        df1 = s[0]
                        constant = df1 + 1
                        sample_f = constant + df2
                        sample_list.append(sample_f)

        # ------------------------------------------- CORRELATION ----------------------------------------------------

        for pattern_cor in pattern_cor_list:
            if pattern_cor:
                expression = pattern_cor.group()
                # print(expression)
                # print(sentences[i])
                pattern_pval = re.search( "(p|P|Ps|ps)\s*(<|>|=)\s*-?\d*\.*\d+(e(-|–)\d+)?", expression)
                reported_pval_exp = pattern_pval.group()
                p_val_list.append(reported_pval_exp)
                s = [float(s) for s in re.findall(r'-?\d+\.?\d*', expression)]
                if len(s) == 3:
                    df2 = 'NULL'
                    df1 = s[0]
                    sample_cor = df1 + 2
                    sample_list.append(sample_cor)

                else:
                    df2 = s[1]
                    df1 = s[0]
                    sample_cor = df1 + 2
                    sample_list.append(sample_cor)

        for pattern_cor_ndf in pattern_cor_no_df_list:
            if pattern_cor_ndf:
                expression = pattern_cor_ndf.group()
                # print(expression)
                # print(sentences[i])
                pattern_pval = re.search( "(p|P|Ps|ps)\s*(<|>|=)\s*-?\d*\.*\d+(e(-|–)\d+)?", expression)
                if pattern_pval:
                    reported_pval_exp = pattern_pval.group()
                    p_val_list.append(reported_pval_exp)
                

    #***********************************************logistic (OR MEANS ODDS RATIO) regression*************************
    
        for pattern_logreg in pattern_logreg_list:
            if pattern_logreg:
                expression = pattern_logreg.group()
                # print(expression)
                pattern_pval = re.search( "(p|P|Ps|ps)\s*(<|>|=)\s*-?\d*\.*\d+(e(-|–)\d+)?", expression)
                if pattern_pval:
                    reported_pval_exp = pattern_pval.group()
                    p_val_list.append(reported_pval_exp)
                
        #********************* HR (hazard ratio) statistics *******************************************
        
        for pattern_hr in pattern_HR_list:
            if pattern_hr:
                expression = pattern_hr.group()
                # print(expression)
                pattern_pval = re.search( "(p|P|Ps|ps)\s*(<|>|=)\s*-?\d*\.*\d+(e(-|–)\d+)?", expression)
                reported_pval_exp = pattern_pval.group()
                p_val_list.append(reported_pval_exp)

        # ----------------------------------- b value in distribution ------------------------------------------------

        for pattern_b in pattern_b_list:
            if pattern_b:
                expression = pattern_b.group()
                # print(expression)
                pattern_pval = re.search( "(p|P|Ps|ps)\s*(<|>|=)\s*-?\d*\.*\d+(e(-|–)\d+)?", expression)
                reported_pval_exp = pattern_pval.group()
                p_val_list.append(reported_pval_exp)


        # ----------------------------------- d value in distribution ------------------------------------------------
        for pattern_d in pattern_d_list:
            if pattern_d:
                expression = pattern_d.group()
                # print(expression)
                pattern_pval = re.search( "(p|P|Ps|ps)\s*(<|>|=)\s*-?\d*\.*\d+(e(-|–)\d+)?", expression)
                reported_pval_exp = pattern_pval.group()
                p_val_list.append(reported_pval_exp)
               

        # ---------------------------------------------- Z-DISTRIBUTION ----------------------------------------------

        for pattern_z in pattern_z_list:
            if pattern_z:
                expression = pattern_z.group()
                pattern_pval = re.search( "(p|P|Ps|ps)\s*(<|>|=)\s*-?\d*\.*\d+(e(-|–)\d+)?", expression)
                reported_pval_exp = pattern_pval.group()
                p_val_list.append(reported_pval_exp)
               

        # ------------------------------------ CHI SQUARE DISTRIBUTION---------------------------------------------

        for pattern_chi in pattern_chi_list:
            if pattern_chi:
                expression = pattern_chi.group()
                # print(expression)
                pattern_pval = re.search( "(p|P|Ps|ps)\s*(<|>|=)\s*-?\d*\.*\d+(e(-|–)\d+)?", expression)
                reported_pval_exp = pattern_pval.group()
                p_val_list.append(reported_pval_exp)
                s = [float(s) for s in re.findall(r'-?\d+\.?\d*', expression)]
                if len(s) == 4:
                    sample_chi = 'NULL'
                    # df1 = s[1]
                else:
                    sample_chi = s[2]
                    # df1 = s[1]
                    # chi_value = s[3]
                    sample_list.append(sample_chi)

        # --------------------------------------------------- Q-DISTRIBUTION ---------------------------------------------

        for pattern_q in pattern_q_list:
            if pattern_q:
                expression = pattern_q.group()
                # print(expression)
                pattern_pval = re.search( "(p|P|Ps|ps)\s*(<|>|=)\s*-?\d*\.*\d+(e(-|–)\d+)?", expression)
                reported_pval_exp = pattern_pval.group()
                p_val_list.append(reported_pval_exp)
               

        #______________________________________________sample size from text_________________________________________________________________________

    for i in range(0, len(sentences) - 1):

            # ---------------------------REGEX FOR P VALUE EXP from sentences ----------------------------

            samplesize_list = re.finditer("(\(| )(n|N|sample size|samplesize| sample size of)\s*[=]\s*\d+", sentences[i])
            

            # append intext sample size to a list names 'intext_samplesize'
            for sample in samplesize_list:
                
                if sample:
                    reported_samplesize = sample.group()
                    intext_samplesize.append(reported_samplesize)
    

    #------------------if no statistical p-values are found search for just intext pvalues________________________-

    # print("P-vals list is:", p_val_list)
    if len(p_val_list) == 0:
        extended_p_val = 1
        for i in range(0, len(sentences) - 1):

            # ---------------------------REGEX FOR P VALUE EXP from sentences ----------------------------
           
           #old p val exp : [p|P]\\s?[<>=]\\s?\\d?\\.\\d+e?[-–]?\\d*
            pattern_p_list = re.finditer("(p|P|Ps|ps)\s*(<|>|=)\s*-?\d*\.*\d+(e(-|–)\d+)?", sentences[i])
            pattern_p_range_list = re.finditer("(p|P)\s*[=<>]\s*\d*.\d*(-|–)\s*\d*.\d*", sentences[i])
            
            # append just pvalues to a list named 'just_pvalues_list'
            for pattern_p in pattern_p_list:
                if pattern_p:
                    reported_pval = pattern_p.group()
                    just_pvalues_list.append(reported_pval)
                   

            # append just pvalues in the form of range to a list named 'just_pvalues_range'
            for pattern_p_range in pattern_p_range_list:
                if pattern_p_range:
                    reported_pval_range = pattern_p_range.group()
                    just_pvalues_range.append(reported_pval_range)

            
                         

        # print("statistical p-values not found, all p-values of pdf", just_pvalues_list)
        p_val_list = just_pvalues_list
        
    
    if len(p_val_list) == 0 and tsv_claim:
        from_claim = get_p_val_darpa_tsv(tsv_claim)
        
        if from_claim:
            p_val_list.append(get_p_val_darpa_tsv(tsv_claim))
    p_val_num_list = []
    for string in p_val_list:
        
        try:
            p_val_num_list.append(float(string.split()[2]))
        except ValueError:
            string = string.replace('–', '-')
            try:
                p_val_num_list.append(float(string.split()[2]))
            except ValueError:
                p_val_num_list.append(float((re.split('[<>=]', string))[-1]))
        except AttributeError:
            pass
        except IndexError:
            # print((re.split('[<>=]', string))[-1])
            p_val_num_list.append(float((re.split('[<>=]', string))[-1]))
            # print("Index error in P-Val script")
            # p_val_num_list = []
    # print("vector of p-value numbers:", p_val_num_list)
    
    intext_sample_num_list = []
    for string in intext_samplesize:
        
        try:
            # print(string)
            intext_sample_num_list.append(float(string.split()[2]))
        except ValueError:
            # string = string.replace('–', '-')
            try:
                intext_sample_num_list.append(float(string.split()[2]))
            except ValueError:
                intext_sample_num_list.append(float((re.split('[=]', string))[-1]))
        except AttributeError:
            pass
        except IndexError:
            # print((re.split('[<>=]', string))[-1])
            intext_sample_num_list.append(float((re.split('[=]', string))[-1]))
    

    if len(p_val_list) > 0 and len(p_val_num_list) > 0:
        num_hypo_test = len(p_val_list)
        if min(p_val_num_list) <= 1:
            real_p_value = min(p_val_num_list)
        # print("Number of hypothesis tested:", num_hypo_test)
        # print("Real p-value:", real_p_value)

        number_significant = 0
        for string in p_val_list:
            try:
                if string.split()[1] == '<' or string.split()[1] == '=':
                    if float(string.split()[2]) <= 0.05:
                        number_significant += 1
            except ValueError:
                string = string.replace('–', '-')
                if float(string.split()[2]) <= 0.05 and (string.split()[1] == '<' or string.split()[1] == '='):
                    number_significant += 1
            except IndexError:
                if any(character in string for character in ['<', '=']):
                    if float((re.split('[<>=]', string))[-1]) <= 0.05:
                        number_significant += 1
        

        if intext_sample_num_list:
            # print("vector of sample sizes", max(sample_list))
            max_sample_size = max(intext_sample_num_list)
            if max(p_val_num_list) >= 1:
                range_p_values = 0
            else:
                range_p_values = max(p_val_num_list) - min(p_val_num_list)
            try:
                if min(p_val_num_list) <= 1:
                    real_p_sign = p_val_list[p_val_num_list.index(min(p_val_num_list))].split()[1]
                    real_p_sign = p_val_sign[real_p_sign]
            except KeyError:
                real_p_sign = 0
            except IndexError:
                real_p_sign = p_val_sign[re.search('[<>=]', p_val_list[p_val_num_list.index(min(p_val_num_list))]).group()]
        elif sample_list and not intext_sample_num_list:

            max_sample_size = max(sample_list)

            if max(p_val_num_list) <= 1:
                range_p_values = max(p_val_num_list) - min(p_val_num_list)
            else:
                range_p_values = 0

            try:
                if min(p_val_num_list) <= 1:
                    real_p_sign = p_val_list[p_val_num_list.index(min(p_val_num_list))].split()[1]
                    real_p_sign = p_val_sign[real_p_sign]
            except KeyError:
                real_p_sign = 0
            except IndexError:
                if min(p_val_num_list) <= 1:
                    real_p_sign = p_val_sign[re.search('[<>=]', p_val_list[p_val_num_list.index(min(p_val_num_list))]).group()]
            

    return (num_hypo_test, real_p_value, real_p_sign, range_p_values, number_significant, max_sample_size, extended_p_val)


from rpy2.robjects.packages import importr
utils = importr('utils')
utils.chooseCRANmirror(ind=1)
utils.install_packages("statcheck")
statcheck = importr("statcheck")


claims_error = 0
count=0
threshold = 0
sample_size_array = []
sample_size_array.append(0)
extend_p_statcheck = 1
real_p_sign_statcheck = 0
real_p_value_statcheck = 0
p_value_range_statcheck = 0
number_significant_statcheck = 0
num_hypo_test_statcheck = 0
number_claims_error = 0
num_p_value_expression = 0


def p_value_sign(p_val):
  global real_p_sign_statcheck
  if(p_val == "<"):
    real_p_sign_statcheck = -1
  elif(p_val == "="):
    real_p_sign_statcheck = 0
  else:
    real_p_sign_statcheck = 1

def sample_size(stat,df_val,df1_val):
  if(stat == "r"):
    if(df_val == "NA"):
      sample_size_statcheck = df_val + 2
      sample_size_array.append(sample_size_statcheck)
    else:
      sample_size_statcheck = df1_val + 2
      sample_size_array.append(sample_size_statcheck)
  elif(stat == "t"):
    if(df_val == "NA"):
      sample_size_statcheck = df_val + 1
      sample_size_array.append(sample_size_statcheck)
    else:
      sample_size_statcheck = df1_val + 1
      sample_size_array.append(sample_size_statcheck)
  elif(stat == "f" or stat == "F"):
    sample_size_statcheck = df_val + df1_val+ 1
    sample_size_array.append(sample_size_statcheck)

def statcheck_calculation(claim):
  p_value = []
  global count, threshold, claims_error, num_hypo_test_statcheck, num_p_value_expression, number_significant_statcheck, extend_p_statcheck, number_claims_error, real_p_value_statcheck, p_value_range_statcheck
  result = statcheck.statcheck(claim)
  if (result):
    for row in result.iter_row():
      p_value.append(tuple(row[7])[0])
      sample_size(tuple(row[1])[0], tuple(row[2])[0],tuple(row[3])[0])
      count=count+1
      if(tuple(row[7])[0]<=0.05):
        threshold+=1
      if (tuple(row[10])[0]):
        pass
      else:
        claims_error+=1
    p_value.sort()
    real_p_value_statcheck = p_value[0]
    p_value_range_statcheck = p_value[count-1] - p_value[0]
    for row in result.iter_row():
      if (tuple(row[7])[0] == p_value[0]):
        p_value_sign(tuple(row[6])[0])
        
        break

    num_hypo_test_statcheck = count
    num_p_value_expression = count
    number_significant_statcheck = threshold
    extend_p_statcheck = 0
    number_claims_error = claims_error
    
  else:
    pass
    
def compare_results(num_hypo_test_sree, num_hypo_test_statcheck):
  if int(num_hypo_test_sree) < int(num_hypo_test_statcheck):
    print("Model: Statcheck")
    print("num_hypo_tested:", num_hypo_test_statcheck,",", "real_p:", real_p_value_statcheck,",", "real_p_sign:", real_p_sign_statcheck,",",
            "p_val_range:", p_value_range_statcheck,",", "num_significant:", number_significant_statcheck,",", "sample_size:", max(sample_size_array),",",
            "extend_p:", extend_p_statcheck,",", "Number of claim_errors:", number_claims_error )
  else:
    print("Model: Sree's Model")
    print("num_hypo_tested:", num_hypo_test_sree,",", "real_p:", real_p_value_sree,",", "real_p_sign:", real_p_sign_sree,",",
            "p_val_range:", range_p_values_sree,",", "num_significant:", number_significant_statcheck, ",","sample_size:", max_sample_size_sree,",",
            "extend_p:", extended_p_val_sree,",", "Number of claim_errors:", number_claims_error)
  
claim = "t(12)=4.3, p=0.01 and f(21,30)=2,3, p<0.02 and F(1,104) = 7.66, p=0.007; omega squared = 0.059."
statcheck_calculation(claim)
num_hypo_test_sree, real_p_value_sree, real_p_sign_sree, range_p_values_sree, number_significant_sree, max_sample_size_sree, extended_p_val_sree = extract_p_values(claim)
compare_results(num_hypo_test_sree, num_hypo_test_statcheck)
