import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
class Reviewers_Utility:
    def __init__(self,df,col1,col2,eta=1, mu=1.2):
        #table contingency between data in col1 and col2
        self.tcontin = pd.crosstab(index=df[col1], columns=df[col2],margins=True)
        aux =self.tcontin.index
        aux = np.array(aux[:-1],dtype=np.float)
        self.v_effort = set(aux)
        aux =self.tcontin.columns
        aux = np.array(aux[:-1],dtype=np.float)
        self.v_quality = set(aux)
        self.rows = len(self.v_effort)
        self.cols = len(self.v_quality)
        self.eta = eta
        self.mu = mu
    
    def get_effort_values(self):
        return self.v_effort
    def get_quality_values(self):
        return self.v_quality

    def pdf_y_e(self,ve,vq):
        if (self.tcontin.at[ve,'All']==0):
            return 0
        else:
            return self.tcontin.at[ve,vq]/self.tcontin.at[ve,'All']
    
    def media_y_e(self,ve):
        m=0.0
        for y in self.v_quality:
            m+=y*self.pdf_y_e(ve,y)*y
        return m
    def f_y_a_mayor(self,ve,a):
        m=0    
        for y in self.v_quality:
            if (a<=y):
                m+=(y-a)*self.pdf_y_e(ve,y)
        return m
    def f_y_a_menor(self,ve,a):
        m=0    
        for y in self.v_quality:
            if (a>=y):
                m+=(y-a)*self.pdf_y_e(ve,y)
        return m
            
    def g_function(self,ve,a):
        Ey_e= self.media_y_e(ve)
        s_lesser = self. f_y_a_menor(ve,a)
        s_bigger = self. f_y_a_mayor(ve,a)
        g_v = Ey_e+self.eta*(self.mu*s_lesser+s_bigger)
        return g_v
        
    def plot_f_y_e(self):
        ax = plt.axes(projection='3d')

        # Data for a three-dimensional line
        
        Z=[]
        for i,x in enumerate(self.v_quality):
            for j,y in enumerate(self.v_effort):
                Z.append(self.tcontin.at[y,x])
       
        X=np.array(list(self.v_quality))
       
        Y=np.array(list(self.v_effort))
        xy = np.array(np.meshgrid(X,Y)).reshape(-1,2)

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(xy[:,0],xy[:,1],Z)
        #ax.plot(xy[:,0],xy[:,1],Z)

        plt.show()  
