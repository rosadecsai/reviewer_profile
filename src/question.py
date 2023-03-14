import pandas as pd
import numpy as np
class Question:
    def __init__(self,line):
        
        aux = line.split(";")
        
        if len(aux)<=1:
           return;
        n=len(aux);
        if aux[n-1][len(aux[n-1])-1]=='\n':
            aux[n-1]=aux[n-1][:-1];
        self.code =aux[0] #code question
        self.txt = aux[1] #question's text
        
        self.col =0;
        factor=ord('Z')-ord('A')+1;
        
        c= 1;
        
        for i in range (len(aux[2])-2,-1,-1):
            self.col += (ord(aux[2][i])-ord('A')+1)*c #excel's column
            c*=factor
        self.col-=1	
      
        self.type= aux[3] #type of answer B=binary D=in range [0,10] T 
        self.number = int(aux[4]) #range or possible answers
        self.answers =[]
        if self.type=='T' or self.type=='B': #if is text

            for i in range(5,len(aux)):
                self.answers.append(aux[i])

    
class Questions:
	def __init__(self,file_codes):
		#read the codes files
		self.qs=dict()
		with open(file_codes) as f:
			lines = f.readlines()
			
			for l in lines:
				if (l!=""):
					Q=Question(l)
					self.qs.update({Q.code:Q});
		self._current_index=0
		self._size=len(self.qs)		
		self._all_codes = list(self.qs.keys());			
	def size(self):
		return len(self.qs)

	def getAnswers(self,df,code,ini=None, fin=None):
		
		if (ini==None):
			ini=1
		if (fin==None):
			fin=len(df)
		d = np.zeros((fin-ini,1))
		aux =None	
		cc= self.qs[code].code
		if (self.qs[code].type=='B'):
			
			aux =pd.DataFrame(data=d,dtype=np.float,columns=[self.qs[code].code])	
			for i in range(ini,fin):
				if df.iloc[i,self.qs[code].col]=="Yes":
					aux.at[i-ini,cc]=1
				else:
					aux.at[i-ini,cc]=0
		elif self.qs[code].type=='T':
			d=np.zeros(((fin-ini),self.qs[code].number))
			cols=[]
			for j in range(0,self.qs[code].number):
				str_idx = cc+"_"+str(j)
				cols.append(str_idx)

			aux =pd.DataFrame(data=d,dtype=np.float,columns=cols)	
			for i in range(ini,fin):
				v=np.zeros(self.qs[code].number)
				#print("Contestaciones ",self.qs[code].answers)
				#buscamos la contestacion entre las posibles 
				for j in range(self.qs[code].number):
					if df.iloc[i,self.qs[code].col]==self.qs[code].answers[j]:
						str_idx = cc+"_"+str(j)
						aux.at[i-ini,str_idx]=1
						
				
		elif self.qs[code].type=='D':
			aux =pd.DataFrame(data=d,dtype=np.float,columns=[self.qs[code].code])	
			for i in range(ini,fin):
				aux.at[i-ini,cc]=float(df.iloc[i,self.qs[code].col]);
	
		return aux		
		#return df.iloc[ini:fin,self.qs[code].col]
	def __iter__(self):
		return self    
	def __next__(self):
		if self._current_index < self._size:
			aux=self._all_codes[self._current_index]
			self._current_index+=1
			return self.qs[aux]
		raise StopIteration	
