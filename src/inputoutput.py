import pandas as pd
import question 
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
########################################################################
def read_survey_codigo(file_survey,file_codes,i=None,f=None):
    """
    From a survey (LimeSurvey), it gets the data in different columns. 
    Arguments:
        *file_survey: name of file with the survey in excel format
        *file_codes:  name of file with the columns to read from the excel data
        *i: initial row to read. A value of none read frome the frist line
        *f: final row to read. A value of none read until the last line
    Return:
        A dataframe withe the data frame
    Example
        df= read_survey_codigo("results-survey354291.xlsx","columnas_survey_answer_sesgo.txt")
    """
    df = pd.read_excel(file_survey,header=None)
    misqs=question.Questions(file_codes);
    #aux = misqs.getAnswers(df,"Q4.1",ini=1, fin=14)
    result=pd.DataFrame()
    for q in misqs:
        aux= misqs.getAnswers(df,q.code,ini=i, fin=f)
        result = pd.concat([result, aux], axis=1)  
        
    return result

########################################################################
def readData(file_survey, file_codes):
    """
    From a survey (LimeSurvey), it gets the data in different columns. 
    Arguments:
        *file_survey: name of file with the survey in excel format
        *file_codes:  name of file with the columns to read from the excel data
    
    Return:
        A dataframe withe the data frame
    Example
        df= readData("results-survey354291.xlsx","columnas_survey_answer_sesgo.txt")
    """
    df=read_survey_codigo(file_survey,file_codes)
    return df

########################################################################

def getSesgo(file_survey, file_codes):  
    """
    Get data associated with the bias answers. Calculate the total bias (see "sesgo" column)
    Arguments:
        *file_survey: name of the file with the survey
        *file_codes: name of the file with the columns to read
    Return:
        A dataframe with bias information
        write in data directory the excel file sesgo.xlsx
    Example:
        df_sesgo=getSesgo("results-survey354291.xlsx","columnas_survey_answer_sesgo.txt")
    """      
    df = readData(file_survey,file_codes)
    #v(Q1)=(1-Q1.1) * (1/5 (Q1.2+Q1.3+Q1.4+Q1.5+Q1.6)) conditions to accept the review
    df.at[:,"v_Q1"]=(1-df["Q1.1"])*(1.0/5.0)*(df["Q1.2"]+df["Q1.3"]+df["Q1.4"]+df["Q1.5"]+df["Q1.6"])
    #v(Q2): time limited
    df.at[:,"v_Q2"]=df["Q2.1"]/10
    #v(Q3): time limited
    df.at[:,"v_Q3"]=df["Q3.1"]/10
    #v(Q4): prior bias 
    df.at[:,"v_Q4"]=(1-df["Q4.1_2"])*(-df["Q4.1_0"]+df["Q4.1_1"])
    #v(Q5): reviewer's reward
    dolares=[0/200.0,10/200.0,50/200.0,100/200.0,150/200.0,200/200.0]
    df.at[:,"v_Q5"]=0
    for pos in range(len(dolares)):
        col = "Q5.1_"+str(pos)
        df["v_Q5"]=df["v_Q5"]+df[col]*dolares[pos]
    df.at[:,"money"]=0   
    df.at[:,"nomoney"]=0   
    #if he/she chose $0
    df["money"]=np.where(df["Q5.1_0"] == 1, 0,1)
    df["nomoney"]=np.where(df["Q5.1_0"] == 1, 1,0)
    
    df.at[:,"sesgo"]=1-1/4*(df['v_Q1']+df['v_Q2']+df['v_Q3']+df['v_Q4'])
    df.to_excel("data/Sesgo.xlsx", sheet_name = "Sesgo")
    return df

##########################################################
def getGoal(file_survey, file_codes):
    """
    Get data associated with the goal answers. Calculate the total goal (see "goal" column)
    Arguments:
        *file_survey: name of the file with the survey
        *file_codes: name of the file with the columns to read
    Return:
        A dataframe with goal information
        write in data directory the excel file goal.xlsx
    Example:
        df_goal=getSesgo("results-survey354291.xlsx","columnas_survey_answer_goal.txt")
    """   
    
    df = readData(file_survey,file_codes)
    
    #a =(1-Q6.6)* 1/5(Q6.1+Q6.2+Q6.3+Q6.4+Q6.5)
    df.loc[df["Q6.6"] == 1, "Q6.1"] = 0
    df.loc[df["Q6.6"] == 1, "Q6.2"] = 0
    df.loc[df["Q6.6"] == 1, "Q6.3"] = 0
    df.loc[df["Q6.6"] == 1, "Q6.4"] = 0
    df.loc[df["Q6.6"] == 1, "Q6.5"] = 0
    #Correlation between variables 
    df_aux = df[["Q6.1","Q6.2","Q6.3","Q6.4","Q6.5","Q6.6"]]  
    #combinations of goal
    df.at[:,"Q6.1_and_Q6.2"]=(df_aux.loc[:,"Q6.1"]==1) & (df_aux.loc[:,"Q6.2"]==1) 
    df["Q6.1_and_Q6.2"]=df["Q6.1_and_Q6.2"].astype(int)
    df.at[:,"Q6.1_or_Q6.2"]=(df_aux.loc[:,"Q6.1"]==1) | (df_aux.loc[:,"Q6.2"]==1) 
    df["Q6.1_or_Q6.2"]=df["Q6.1_or_Q6.2"].astype(int)

    df.at[:,"Q6.1_and_Q6.3"]=(df_aux.loc[:,"Q6.1"]==1) & (df_aux.loc[:,"Q6.3"]==1) 
    df["Q6.1_and_Q6.2"]=df["Q6.1_and_Q6.3"].astype(int)
    df.at[:,"Q6.1_or_Q6.3"]=(df_aux.loc[:,"Q6.1"]==1) | (df_aux.loc[:,"Q6.3"]==1) 
    df["Q6.1_or_Q6.2"]=df["Q6.1_or_Q6.3"].astype(int)    

    df.at[:,"Q6.2_and_Q6.3"]=(df_aux.loc[:,"Q6.2"]==1) & (df_aux.loc[:,"Q6.3"]==1) 
    df["Q6.2_and_Q6.3"]=df["Q6.2_and_Q6.3"].astype(int)
    df.at[:,"Q6.2_or_Q6.3"]=(df_aux.loc[:,"Q6.2"]==1) | (df_aux.loc[:,"Q6.3"]==1) 
    df["Q6.2_or_Q6.3"]=df["Q6.2_or_Q6.3"].astype(int)

    df.at[:,"Q6.1_and_Q6.2_and_Q6.3"]=(df_aux.loc[:,"Q6.1"]==1) & (df_aux.loc[:,"Q6.2"]==1) & (df_aux.loc[:,"Q6.3"]==1) 
    df["Q6.1_and_Q6.2_and_Q6.3"]=df["Q6.1_and_Q6.2_and_Q6.3"].astype(int)
    df.at[:,"Q6.1_or_Q6.2_or_Q6.3"]=(df_aux.loc[:,"Q6.1"]==1) | (df_aux.loc[:,"Q6.2"]==1) | (df_aux.loc[:,"Q6.3"]==1) 
    df["Q6.1_or_Q6.2_or_Q6.3"]=df["Q6.1_or_Q6.2_or_Q6.3"].astype(int)    
    #print(df_aux.head())
    
    print("Means")
    print(df_aux.mean(axis=0))
    print("Variance ")
    print(df_aux.var(axis=0))
    print("Correlation ")
    print(df_aux.corr(method='kendall'))
    #weights
    f=np.zeros(5)
    n=len(df)
    
    f[0]=0.75
    f[1]=0.1
    f[2]=0.05
    f[3]=0.05
    f[4]=0.05
    
    df.at[:,"goal"]=(1-df['Q6.6'])*(df['Q6.1']*f[0]+df['Q6.2']*f[1]+df['Q6.3']*f[2]+df['Q6.4']*f[3]+df['Q6.5']*f[4])
    df.to_excel("data/Goal.xlsx", sheet_name = "Goal")
    return df

####################################################

def getEffort(file_survey, file_codes):
    """
    Get data associated with the effort answers. Calculate the total effort (see "effort" column)
    Arguments:
        *file_survey: name of the file with the survey
        *file_codes: name of the file with the columns to read
    Return:
        A dataframe with effort information
        write in data directory the excel file effort.xlsx
    Example:
        df_effort=getSesgo("results-survey354291.xlsx","columnas_survey_answer_effort.txt")
    """   

    df = readData(file_survey,file_codes);
    print(df)   
    df.at[:,'effort']=df['Q7.1']/10.0
    df.to_excel("data/effort.xlsx", sheet_name = "effort")
    return df

####################################################

def getQuality(file_survey, file_codes):
    """
    Get data associated with the quality answers. Calculate the total quality (see "quality" column)
    Arguments:
        *file_survey: name of the file with the survey
        *file_codes: name of the file with the columns to read
    Return:
        A dataframe with quality information
        write in data directory the excel file quality.xlsx
    Example:
        df_quality=getSesgo("results-survey354291.xlsx","columnas_survey_answer_quality.txt")
    """   
    
    df = readData(file_survey,file_codes);
    #Q8.1 Q9.1 Q10.1 Q11.1
    df=df.fillna(0) 

    f1=0.5
    fres=0.5/3
    df.loc[:,'quality']=df['Q8.1']/10*f1+(df["Q9.1"]/10+df["Q10.1"]/10+df["Q11.1"]/10)*fres
    df.to_excel("data/quality.xlsx", sheet_name = "quality")    
    return df 
####################################################

def getSatisfaction(file_survey, file_codes):
    """
    Get data associated with the quality answers. Calculate the total quality (see "quality" column)
    Arguments:
        *file_survey: name of the file with the survey
        *file_codes: name of the file with the columns to read
    Return:
        A dataframe with quality information
        write in data directory the excel file quality.xlsx
    Example:
        df_satisfaction=getSesgo("results-survey354291.xlsx","columnas_survey_answer_satisfaction.txt")
    """   
    
    df = readData(file_survey,file_codes);
    #Q9.1 and Q10.1
    
    return df 
