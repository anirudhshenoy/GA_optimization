import openpyxl
from openpyxl.styles import Alignment
from openpyxl import Workbook
import numpy as np
import tkinter as tk
import random
import math
from tkinter import filedialog
import warnings
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning) 
np.set_printoptions(precision=3,suppress=True)

params = [500, 0.35, 200, 5, 50]
#plt.axis([0, 260, 0, 2.6])
#plt.ion()
#GA Parameters
# [Init pop (pop=100), mut rate (=5%), num generations (250), chromosome/solution length (3), # winners/per gen]

b_const=[0.5,1.75]
c_const=[0.1,0.4]
alpha_const=[0,3]
airfoil_const=[0,34]          #1468 for General AFs
l_t_const=[0.6,1.7]             #From CG to C/4_t
i_t_const=[-10,+10]                 #Tail setting angle
E_0=0                         #Downwash angle   3.5
dE_dA=0.1                       #Downwash slope 
CM_ac_wb=-0.277
CM_cg_const=0.05
h_h_ac_w=0                    #Added for consistency
c_wing=0.269
b_wing=2.904
S_wing=c_wing*b_wing
wing_airfoil=452
alpha_wing=2.5


rho=1.227
v=10
e1=0.85
e=0.85
pi=3.1415


#Open XLS for Airfoil Data
wb = openpyxl.load_workbook('C:/Users/Aniru_000/Desktop/TD-1/Airfoil/s1223/airfoil/MasterPolarsFlat/airfoilpolars_master_flat.xlsx')
wb2 = openpyxl.load_workbook('C:/Users/Aniru_000/Desktop/TD-1/Airfoil/s1223/airfoil/tail_foil_naca/Inverted/Polars/airfoilpolars_master.xlsx')
print ("Opened File")
sheet = wb.get_sheet_by_name('slopes')                #Change to index based
print ("Opened Sheet")
slopes=[]
intercepts=[]
a_0=[]


airfoil_names=[]


for cellObj in sheet.columns[0]:
	airfoil_names.append(cellObj.value)
	
for cellObj in sheet.columns[1]:
	slopes.append(cellObj.value)

for cellObj in sheet.columns[2]:
	intercepts.append(cellObj.value)

for i in range(len(slopes)):
        if slopes[i]==0:
            a_0.append(0)
        else:  
            a_0.append((-intercepts[i]/slopes[i]))


	
AR=(b_wing**2)/S_wing
a_wing=slopes[int(wing_airfoil)]/(pi*e1*AR)
a_wing=slopes[int(wing_airfoil)]/(1+(57.3*a_wing))
#alpha_wing=alpha_wing-a_0[wing_airfoil]

slopes=[]
intercepts=[]
airfoil_names=[]
sheet = wb2.get_sheet_by_name('slopes')
for cellObj in sheet.columns[0]:
	airfoil_names.append(cellObj.value)
	
for cellObj in sheet.columns[1]:
	slopes.append(cellObj.value)

for cellObj in sheet.columns[2]:
	intercepts.append(cellObj.value)


#[b c i_t AF l_t]
def fitness(pop):
    #Aliases        
    b_pop=pop[0]
    c_pop=pop[1]
    i_pop=pop[2]
    AF_pop=pop[3]
    l_pop=pop[4]
    

    #Wing Dimensions
    tail_area=b_pop*c_pop
    AR_tail=(b_pop**2)/tail_area

    #Slope Correction    
    a_new=slopes[int(AF_pop)]/(pi*e1*AR_tail)
    a_new=slopes[int(AF_pop)]/(1+(57.3*a_new))
    #a_new=slopes[int(AF_pop)]
    #cl=intercepts[int(AF_pop)]+(a_new*(i_pop-E_0))
    cl=a_new*alpha_wing*(1-dE_dA)-(a_new*(i_pop+E_0))
    #lift=0.5*rho*(v**2)*tail_area*cl
    #cd_i=(cl**2)/(pi*e*AR)
    #drag=0.5*rho*(v**2)*tail_area*cd_i
    
    #Lift Calculation
    
    V_h=(l_pop*tail_area)/(S_wing*c_wing)
    #part3=V_h*a_new*(i_pop+E_0)
    #print (part3)
    #part2=a_wing*alpha_wing*(-((V_h*a_new)/a_wing)*(1-dE_dA))
    #print(part2)
    #CM_cg=CM_ac_wb+part2+part3
    CM_cg=CM_ac_wb-(V_h*cl)
    
    #Drag Calculation
  

    #Fitness Value Calculations                                                         #Play around with Lift_fit parameters for convergence
    cm_fit=70*math.exp(-(((CM_cg-CM_cg_const)*1000)**2)/(2*1000**2))                            #Gaussian function centered around lift_constant, A controls height
    fit=cm_fit                                                          #stall angle characteristics  Minimize moment


    return fit
                            
def final_fitness(pop):
    b_pop=pop[0]
    c_pop=pop[1]
    i_pop=pop[2]
    AF_pop=int(pop[3])
    l_pop=pop[4]

    tail_area=b_pop*c_pop
    AR_tail=(b_pop**2)/tail_area

    #Slope Correction    
    a_new=slopes[int(AF_pop)]/(pi*e1*AR_tail)
    a_new=slopes[int(AF_pop)]/(1+(57.3*a_new))
    cl=a_new*alpha_wing*(1-dE_dA)-(a_new*(i_pop+E_0))

    #Lift Calculation
    
    V_h=(l_pop*tail_area)/(S_wing*c_wing)
    #part3=V_h*a_new*(i_pop+E_0)
    #print (part3)
    #part2=a_wing*alpha_wing*(-((V_h*a_new)/a_wing)*(1-dE_dA))
    #print(part2)
    #CM_cg=CM_ac_wb+part2+part3
    CM_cg=CM_ac_wb-(V_h*cl)
        
   
    print("Slope: "+str(a_new))
    print("Span: "+str(b_pop))
    print("Chord: "+str(c_pop))
    print("Tail Set angle: "+str(i_pop))
    print("Moment Arm: "+str(l_pop))
    print("CM: "+str(CM_cg))
    
    





#First Generation Initialization
b =np.random.choice(np.arange(b_const[0],b_const[1],step=0.01),size=(params[0],1),replace=True)
c =np.random.choice(np.arange(c_const[0],c_const[1],step=0.01),size=(params[0],1),replace=True)
i_t =np.random.choice(np.arange(i_t_const[0],i_t_const[1],step=0.5),size=(params[0],1),replace=True)
airfoil =np.random.choice(np.arange(airfoil_const[0],airfoil_const[1],step=1),size=(params[0],1),replace=True)
l_t=b =np.random.choice(np.arange(l_t_const[0],l_t_const[1],step=0.1),size=(params[0],1),replace=True)


curPop=np.concatenate((b,c,i_t,airfoil,l_t),1)
nextPop = np.zeros((curPop.shape[0], curPop.shape[1]))
fitVec = np.zeros((params[0], 2))
best_fit_overall=-np.inf


#Looping over Generations


for j in range (params[2]):      #params[2]
        for i in range(params[0]):
                             fitVec[i,0]=i
                             fitVec[i,1]=fitness(np.array([curPop[i,0],curPop[i,1],curPop[i,2],curPop[i,3],curPop[i,4]]))

        winners = np.zeros((params[4], params[3]))
        best_fit=max(fitVec[:,1])
        best_cand=np.argmax(fitVec[:,1])
        print(curPop[best_cand])
        if best_fit>best_fit_overall:
               best_soln = curPop[np.argmax(fitVec[:,1])]
               best_b=best_soln[0]
               best_fit_overall=best_fit
               
        print("(Gen: #%s) Best Fitness: %s" % (j,best_fit))
        print("Airfoil: "+ airfoil_names[int(curPop[best_cand,3])])
        #print(curPop)
        #Hall of Fame
        for n in range(len(winners)):
                             selected = np.random.choice(range(len(fitVec)), params[4]/2, replace=False)
                             wnr = np.argmax(fitVec[selected,1])
                             winners[n] = curPop[int(fitVec[selected[wnr]][0])]


        nextPop[:len(winners)] = winners
        #print(winners)
        #Crossover
        nextPop[len(winners):] = np.array([np.array(np.random.permutation(np.repeat(winners[:, x], ((params[0] - len(winners))/len(winners)), axis=0))) for x in range(winners.shape[1])]).T

        #Mutation
        curPop = np.multiply(nextPop, np.matrix([np.float(np.random.uniform(0.5,1.5)) if random.random() < params[1] else 1 for x in range(nextPop.size)]).reshape(nextPop.shape))



        #Ensure all values are within constraints
        for k in range(params[0]):
                            curPop[k,3]=math.floor(math.fabs(curPop[k,3]))
                            if curPop[k,3]>airfoil_const[1]:
                                    curPop[k,3]=random.randint(0,airfoil_const[1])
                            if curPop[k,2]>i_t_const[1] or curPop[k,2]<i_t_const[0]:
                                    curPop[k,2]=np.random.uniform(i_t_const[0],i_t_const[1])
                            if curPop[k,1]>c_const[1] or curPop[k,1]<c_const[0]:
                                    curPop[k,1]=np.random.uniform(c_const[0],c_const[1])
                            if curPop[k,0]>b_const[1] or curPop[k,0]<b_const[0]:
                                    curPop[k,0]=np.random.uniform(b_const[0],b_const[1])
                            if curPop[k,4]>l_t_const[1] or curPop[k,4]<l_t_const[0]:
                                    curPop[k,4]=np.random.uniform(l_t_const[0],l_t_const[1])

                                       


print("Best Sol'n:\n%s" % (best_soln))
print("Fit: " +str(best_fit_overall))
print("Airfoil: "+airfoil_names[int(best_soln[0,3])])
final_fitness(np.array([best_soln[0,0],best_soln[0,1],best_soln[0,2],best_soln[0,3],best_soln[0,4]]))
