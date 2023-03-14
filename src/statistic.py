from scipy.stats import chi2_contingency
import pandas as pd
#ANOVA
import statsmodels.api as sm
from statsmodels.formula.api import ols
from bioinfokit.analys import stat
#MANOVA
from dfply import *
from statsmodels.multivariate.manova import MANOVA

#PCA analysis
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
#plot
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import plotly.graph_objects as go
########################################################################


def getTestChiSquare(df,independent,dependents):
    """
    Applies the chi square test to the input data. 
    Arguments:
        *df: dataframe with the data
        *independents: column with the indpendent variable
        *dependents: columns with the dpendents variable
    Return: A pair with the result of the test (statistic,pvalue) and the contingency table
    Example
        res,tc=getTestChiSquare(df_test,"money",["Q61","Q62"])
    """
    #chi_square test for signification
    a=[df[dependents[i]] for i in range(len(dependents))]
    obs = pd.crosstab(index=df[independent], columns=a)
    res = chi2_contingency(obs)
    return res,obs
########################################################################
def getANOVA(df):
    """
    Apply the ANOVA test to the columns in a dataframe. 
    ANOVA test has as null hypothesis that the columns has not significative differences
    Arguments:
        *df: data frame with the data
    
    Example:

    URL:
    https://www.kaggle.com/code/pasuvulasaikiran/anova

    """
    # reshape the d dataframe suitable for statsmodels package 
    df_melt = pd.melt(df.reset_index(), id_vars=['index'], value_vars=df.columns)
    # replace column names
    df_melt.columns = ['index', 'treatments', 'value']
    model = ols('value ~ C(treatments)', data=df_melt).fit()
    
    res = stat()
    res.anova_stat(df=df_melt, res_var='value', anova_model='value ~ C(treatments)')
    print(res.anova_summary)

    #Interpretation:The p value obtained from ANOVA analysis if is significant (p < 0.05) then
    #there is different between the groups

    # perform multiple pairwise comparison (Tukey's HSD)
    # unequal sample size data, tukey_hsd uses Tukey-Kramer test
    res = stat()
    res.tukey_hsd(df=df_melt, res_var='value', xfac_var='treatments', anova_model='value ~ C(treatments)')
    print(res.tukey_summary)


########################################################################

def getMANOVA(df,independent,dependent,plotTable=False):
    """
    Applies the MANOVA test (multivariate ANOVA) to the input data. 
    Arguments:
        *df: dataframe with the data
        *independents: column with the indpendent variable
        *dependents: columns with the dpendents variable
    Return:
    Example
       getMANOVA(df_test,"money",["Q61","Q62"])
    """
    a=[df[dependent[i]] for i in range(len(dependent))]
    obs = pd.crosstab(index=df[independent], columns=a)
    print("Cross Table")
    print(obs)
    #print info for every variable
    texto=""
    for i in range(len(dependent)):
        c=dependent[i]
        # summary statistics for dependent variables
        print("Dependent variable ", c)
        aux=df >> group_by(X[independent]) >> summarize(n=X[c].count(), mean=X[c].mean(), std=X[c].std())
        print(aux)
        
        texto=texto+ dependent[i]+ " + "    
    texto=texto[:-3]
    texto=texto+" ~ "+independent    
    
    fit = MANOVA.from_formula(texto, data=df)
    print(fit.mv_test())
    #p.e Pill's test give a value less than 0.05 at the  95% we can 
    # say that the variables are not indpendent
    
    if (plotTable==True):
        print(obs.columns)
        print(obs.index)
        obs.index=["Reviewer's compensation:\n \$0","Reviewer's compensation:\n between \$10 and \$200" ]
        obs.columns.names=["Q1.1","Q2.3"]
        obs.columns.set_levels(["No","Yes"],level=0,inplace=True)
        obs.columns.set_levels(["No","Yes"],level=1,inplace=True)
        font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 14}
        plt.rc('font', **font)
        barplot = obs.plot.bar(rot=0)
        #barplot.legend(loc='upper right', bbox_to_anchor=(1., 1.))
        
      
        plt.show()
    
    
 ########################################################################
def analysis_PCA(datos):
    """
    Analysis Principal Components (PCA) with data's scaling 
    Arguments:
        *datos: data with the variables to analyze
    Return   
    Example:
        analysis_PCA(df)  df can have "Q6.1,Q6.2,Q6.3,Q6.4,Q6.4"
    """
    
    pca_pipe = make_pipeline(StandardScaler(), PCA())
    pca_pipe.fit(datos)
    # The training model is extracted from the pipeline
    modelo_pca = pca_pipe.named_steps['pca']
    #build a dataframe with the principal components
    pd.DataFrame(
    data    = modelo_pca.components_,
    columns = datos.columns,
    index   = ['PC1', 'PC2', 'PC3', 'PC4','PC5']
    )
    #PLOT info
    # Heatmap componentes
    # ==============================================================================
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(5, 2))
    componentes = modelo_pca.components_
    plt.imshow(componentes.T, cmap='viridis', aspect='auto')
    plt.yticks(range(len(datos.columns)), datos.columns)
    plt.xticks(range(len(datos.columns)), np.arange(modelo_pca.n_components_) + 1)
    plt.grid(False)
    plt.colorbar();
    # Percentage of variance explained by each component
    # ==============================================================================
    print('----------------------------------------------------')
    print('Percentage of variance explained by each component')
    print('----------------------------------------------------')
    print(modelo_pca.explained_variance_ratio_)

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6, 4))
    ax.bar(
        x      = np.arange(modelo_pca.n_components_) + 1,
        height = modelo_pca.explained_variance_ratio_
    )

    for x, y in zip(np.arange(len(datos.columns)) + 1, modelo_pca.explained_variance_ratio_):
        label = round(y, 2)
        ax.annotate(
        label,
        (x,y),
        textcoords="offset points",
        xytext=(0,10),
        ha='center'
        )

    ax.set_xticks(np.arange(modelo_pca.n_components_) + 1)
    ax.set_ylim(0, 1.1)
    ax.set_title('Percentage of variance explained by each component')
    ax.set_xlabel('Principal component')
    ax.set_ylabel('Per. Variance Explained');
         
########################################################################
def plot_histo(df,name_col,nbins):
    """
    Draw the histogram of a column in a data frame with several bins.
    Arguments:
        *df: data frame
        *name_col: name of the column with the data
        *nbins: number of bins in the histogram
    """
    ax = df.hist(column=name_col, bins=nbins, grid=False, figsize=(12,8), color='#86bf91', zorder=2, rwidth=0.9)
    ax = ax[0]
    for x in ax:
        # Despine
        x.spines['right'].set_visible(False)
        x.spines['top'].set_visible(False)
        x.spines['left'].set_visible(False)

        # Switch off ticks
        x.tick_params(axis="both", which="both", bottom="off", top="off", labelbottom="on", left="off", right="off", labelleft="on")

        # Draw horizontal axis lines
        vals = x.get_yticks()
        for tick in vals:
            x.axhline(y=tick, linestyle='dashed', alpha=0.4, color='#eeeeee', zorder=1)

        # Remove title
        x.set_title("")

        # Set x-axis label
        x.set_xlabel(name_col, labelpad=20, weight='bold', size=12)

        # Format y-axis label
        x.yaxis.set_major_formatter(StrMethodFormatter('{x:,g}'))
    plt.show()
#########################################################################
def getCrossTab(df_aux,col1,col2,file_output,writetest=False ):
    """
    Draw the contingency table between two variables and get the results of chi-squared test
    Arguments:
        *df_aux: data frame with the data
        *col1: name of column in the data frame with the information of variable 1 
        *col2: name of column in the data frame with the information of variable 2
        *file_output: name of the file with the drawing of the contingency table
        *writetest: if True  the result of the test chi-squares is write in the drawing
    Return:
        the result of the chi-square        
    Example
        getCrossTab(df,"money","Q6.1", data/sesgo_goal/)        
    """
    #chi_square test for signification
    obs = pd.crosstab(index=df_aux[col1], columns=df_aux[col2])
    res = chi2_contingency(obs)
    texto_test=""
    if writetest==True:
        stat='{0:.2f}'.format(res[0])
        pvalue='{0:.2f}'.format(res[1])
        texto_test = "Chi-Squared<br> statistic: "+stat+" p-value: "+pvalue

    info_size=[]
    str_dest=col2
    str_source=col1
    info_size.append( df_aux[(df_aux[str_source]==0) & (df_aux[str_dest]==0)].count()[str_source])
    info_size.append( df_aux[(df_aux[str_source]==1) & (df_aux[str_dest]==0)].count()[str_source])
    info_size.append( df_aux[(df_aux[str_source]==0) & (df_aux[str_dest]==1)].count()[str_source])
    info_size.append( df_aux[(df_aux[str_source]==1) & (df_aux[str_dest]==1)].count()[str_source])
    aux_size ={(0,0):info_size[0],(1,0):info_size[1],(0,1):info_size[2],(1,1):info_size[3]}
    
    print(info_size)
    ques={ "Q6.1":"Quality control","Q6.2":"Helping the profession","Q6.3":"Staying up-to-date",
   "Q6.4":"Networking opportunities","Q6.5":"Just enjoying it","Q4.1_0":"Write a review report for a<br> high difficulty manuscript",
   "Q4.1_1":"Write a report to secure <br>a peer-reviewed grant","Q4.1_2":"Both of the above two options",
   "money":"Reviewer's compensation: between &#36;10 and &#36;200","nomoney":"Reviewer's compensation: &#36;0",
   "Q6.1_and_Q6.2":"Quality control and<br> Helping the profession",
   "Q6.1_and_Q6.3":"Quality control and <br> Staying up-to-date",
   "Q6.2_and_Q6.3":"Helping the profession and <br> Staying up-to-date",
   "Q6.1_and_Q6.2_and_Q6.3":"Quality control and <br>Helping the profession <br> Staying up-to-date",
   "Q6.1_or_Q6.2":"Quality control or<br> Helping the profession",
   "Q6.1_or_Q6.3":"Quality control or <br> Staying up-to-date",
   "Q6.2_or_Q6.3":"Helping the profession or<br> Staying up-to-date",
   "Q6.1_or_Q6.2_or_Q6.3":"Quality control or <br>Helping the profession or<br> Staying up-to-date"}
    
    color={(0,0):'rgb(200, 200, 214)',(1,0): 'rgb(255, 200, 200)', (0,1):'rgb(200, 250, 201)', (1,1):'rgb(255, 185, 54)'}
    tamano =list(aux_size[(u,v)] for u,v in zip(df_aux[str_source],df_aux[str_dest]))
    mitext =list(str(aux_size[(u,v)]) for u,v in zip(df_aux[str_source],df_aux[str_dest]))           
    colorin=list(color[(u,v)] for u,v in zip(df_aux[str_source],df_aux[str_dest]))
    text_dest=ques[str_dest]
    text_source=ques[str_source]
    
    print("max =",df_aux[str_dest].max())
    print("min =",df_aux[str_dest].min())
    fig = go.Figure(data=[go.Scatter(
    x=df_aux[str_source], y=df_aux[str_dest],
    mode="markers+text",
   
    text=mitext,
    marker=dict(
        color=colorin,
        size=tamano
    ))
    ])
    fig.update_traces( textfont_size=30)
    fig.update_layout(
        title="",
        xaxis=dict(
            title=text_source,
            
            gridcolor='white',
            tickangle= 0,
            tickmode = 'array',
            tickvals = [0,1],
            ticktext = ['No','Yes'],
            
        ),
        yaxis=dict(
            #title='Q6.2: Helping the profession',
            title=text_dest,
            gridcolor='white',
            gridwidth=0.025,
            tickmode = 'array',
            tickvals = [0.0,1.0],
            ticktext = ['No', 'Yes'],
        ),
        font=dict(
            family="Courier New, monospace",
            size=30,
            color="Black"
        ),
        
        paper_bgcolor='rgb(253, 253, 253)',
        plot_bgcolor='rgb(243, 243, 243)',
    )

    fig.update_layout(
        height=800,
        title_text=texto_test
    )
    #fig.show()
    scale_seq = 1,2
    fig.write_image(file_output,scale=scale_seq,width=1200, height=800 )
    return res
    
