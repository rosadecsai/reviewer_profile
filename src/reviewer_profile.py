import pandas as pd
import os
import plotly.graph_objects as go
import numpy as np
import reviewers_utility as ru
from statistic import *
from inputoutput import *


def getCrossTabGlobal(dict_dfs,parescros,path):
    """
    Get cross table between different questions and chi-test contingecy
    Arguments:
     *dict_dfs: dictionay with the different data frames
     *parescros: pair of names representing the information to analyze
     *path: directory output
    Example:
     getCrossTabGlobal(dataframes,pares_cross,path_reference)

    """
    #possibles columns. In the paper Q4 is Q2 and Q6 is Q1
    dic_columns={"money":set(["money","nomoney"]),
                 "sesgo":set(["Q4.1_0","Q4.1_1","Q4.1_2"]),
                 "goal":set(["Q6.1","Q6.2","Q6.3","Q6.4","Q6.5"])
                 }
    
    for x in parescros:
        dir=path+x[0]+"_"+x[1]+"/"

        if not os.path.exists(dir):
            os.mkdir(dir)
        #open the file to store the chi-squared results    
        aux = dir+"chi_results.txt"
        fchi=open(aux,'w')
        #create a dataframe with the two input dataframes
        columns1 = dic_columns[x[0]]
        columns2 = dic_columns[x[1]]
        for c1 in columns1:
            df_analysis=pd.DataFrame()
            df_analysis.at[:,c1]=dict_dfs[x[0]][c1]
            for c2 in columns2:
                if (c1!=c2):
                    file_name = dir+c1+"VS"+c2+".png"
                    df_analysis.at[:,c2]=dict_dfs[x[1]][c2]
                    res_chi=getCrossTab(df_analysis,c1,c2,file_name )
                    txt =c1+" "+c2+" "+str(res_chi[0])+" "+str(res_chi[1])+"\n"
                    fchi.write(txt)
        fchi.close()            

def plot_gain_utility(df,eta,mu,betas,cs):
    """
    Plot gain in utility to mak a high-effort agains a low effort give a intial goal
    Arguments:
     *df: data set with the answer of the survey
     *eta: factor of satisfaction/insatisfaction
     *mu: epresenting 𝜇 > 1 the reviewer’s loss-aversion coefficient
     *betas: list of present bias values
     *cs: list of cost to do a high effort
    Result: the set of plots are saved in data/gain_utility
    """
    #get the distribution f(y|e)
    Ru = ru.Reviewers_Utility(df,'effort','quality',eta,mu)
    #plot f(y|e)
    #Ru.plot_f_y_e()
    
    #get the goal values in the survey
    a_values=sorted(set(df_result['goal']))
    #get the effort values in the survey
    e_values = Ru.get_effort_values()
    g_values=dict()
    #for each effort value and goal value we get the g(e,a)
    for e in e_values:
        g_values.update({e:[]})
        for a in a_values:
            g_values[e].append(Ru.g_function(e,a))
    
    #fix a bias present
    #beta = 0.425
    #fix a cost of high-effort 
    #c=0.2
    for beta in betas:
        for c in cs:
            ev = list(e_values)
            e_menor = ev[0]
            e_mayor = ev[len(ev)-1]
            print("Loww effort",ev[0])
            print("High effort",ev[len(ev)-1])
            y_values=[]
            pos=0
            for a in a_values:
                y_values.append( beta*(g_values[e_mayor][pos]-g_values[e_menor][pos])-c)
                pos+=1
            plt.rc('text', usetex=True)         
            fig, ax = plt.subplots(figsize=(6, 4), tight_layout=True)   
            ax.plot(list(a_values),y_values)
            ax.set_ylabel(r"$\beta (g( \overline{e},a)-g( \underline{e},a))-c$", fontsize=24)
            ax.set_xlabel("a", fontsize=24)
            strtitle=r"$\beta="+str(beta)+"$ c="+str(c)
            ax.set_title(strtitle,fontsize=28)
            plt.xticks(fontsize=18, rotation=0)
            plt.yticks(fontsize=18, rotation=0)
            file_name = "data/gain_utility/gu"+str(beta)+"_"+str(c)+".png"
            plt.savefig(file_name)
            #plt.show()

if __name__ == '__main__':
    
    file_survey = "data/data_input/results-survey354291.xlsx"
    file_codes = "data/data_input/columnas_survey_answer_sesgo.txt"
    file_codes_goal = "data/data_input/columnas_survey_answer_goal.txt"
    file_codes_effort = "data/data_input/columnas_survey_answer_esfuerzo.txt"
    file_codes_quality = "data/data_input/columnas_survey_answer_quality.txt"
   
    df_sesgo=getSesgo(file_survey, file_codes)
    df_effort=getEffort(file_survey, file_codes_effort)
    df_goal=getGoal(file_survey, file_codes_goal)
    df_quality=getQuality(file_survey, file_codes_quality)
    
    #save calculated data
    df_result =pd.DataFrame()
    df_result.at[:,'goal']=df_goal['goal']
    df_result.at[:,'sesgo']=df_sesgo['sesgo']
    df_result.at[:,'effort']=df_effort['effort']
    df_result.at[:,"quality"]=df_quality["quality"]
    df_result.to_excel("data/DataResult.xlsx")
    #uncomment the following sections depending on what you want to get
    #Remember Q6 in the paper is Q1 and Q4 in the paper is Q2

    #Apply ANOVA to see between goal there is differeces significatives
    # print("########################################")
    # print("ONE WAY ANOVA test for Q6 question")
    # print("########################################")
    #getANOVA(df_goal[["Q6.1","Q6.2","Q6.3","Q6.4","Q6.5"]])
    # input()
    
    
    #crosstab between different questions
    # print("########################################")
    # print("Cross Table between goal, sesgo and reviewr's reward")
    # print("########################################")
    # path_reference = "./data/"
    # pares_cross=[("goal","goal"),("money","goal"),("money","sesgo"),("sesgo","goal")]
    # dataframes={"sesgo":df_sesgo,"goal":df_goal,"money":df_sesgo}
    # getCrossTabGlobal(dataframes,pares_cross,path_reference)


    #MANOVA 
    #significave diference between reward and goal
    ###########################################
    # print("########################################")
    # print("dependency with more one variable")
    # print("########################################")
    # df_test=pd.DataFrame()
    # df_test.at[:,"Q61"]=df_goal["Q6.1"]
    # df_test.at[:,"Q62"]=df_goal["Q6.2"]
    # df_test.at[:,"Q63"]=df_goal["Q6.3"]
    # df_test.at[:,"Q64"]=df_goal["Q6.4"]
    # df_test.at[:,"Q65"]=df_goal["Q6.5"]
    # df_test.at[:,"nomoney"]=df_sesgo["nomoney"]
    # df_test.at[:,"Q410"]=df_sesgo["Q4.1_0"]
    # df_test.at[:,"Q411"]=df_sesgo["Q4.1_1"]
    # df_test.at[:,"Q412"]=df_sesgo["Q4.1_2"]
    # df_test.at[:,"money"]=df_sesgo["money"]
    #for simple goals 
    #getANOVA(df_test)
    #getANOVA(df_test[["money","Q61","Q62","Q63","Q64","Q65"]])
    #getANOVA(df_test[["nomoney","Q61"]])
    #getMANOVA(df_test,"money",["Q61","Q62"])
    #for combinations of goals p.e (Q61,Q62) (Q61,Q63) 
    #getMANOVA(df_test,"money",["Q61","Q62"])

    #Analize if Q6.1 joint to Q6.2 and money
    #getMANOVA(df_test,"money",["Q61","Q62"],True)

    #Analize if Q6.1 joint to Q6.2 and Q4.1_0 or Q4.1_1 or Q4.1_2
    #getMANOVA(df_test,"money",["Q61","Q412"],True)
    
    
   




    
    #####################################################################
    ###########################################
    print("########################################")
    print("Creating plot of gain utility vs initial goal")
    print("########################################")
    plot_gain_utility(df_result,eta=2.13,mu=1.2,betas={0.1,0.15,0.25,0.3},cs={0.1,0.15,0.2,0.25})
   