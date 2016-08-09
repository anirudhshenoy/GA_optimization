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

params = [500, 0.05, 200, 5, 50]
#plt.axis([0, 260, 0, 2.6])
#plt.ion()
#GA Parameters
# [Init pop (pop=100), mut rate (=5%), num generations (250), chromosome/solution length (3), # winners/per gen]

b_const=[0.1,3]
c_const=[0.1,0.4]
taper_const=[0.5,0.9]
alpha_const=[0,3]
airfoil_const=[0,635]          #1468 for General AFs
AR_const=5
lift_const=49
area_const=1
rho=1.227
v=10
e1=0.9
e=0.85
pi=3.1415


#Open XLS for Airfoil Data
wb = openpyxl.load_workbook('C:/Users/Aniru_000/Desktop/TD-1/Airfoil/s1223/airfoil/MasterPolarsFlat/airfoilpolars_master_flat.xlsx')
print ("Opened File")
sheet = wb.get_sheet_by_name('slopes')                #Change to index based
print ("Opened Sheet")
slopes=[]
intercepts=[]
temp=[]                                       #Please fix this shit
cd_d2=[]
cd_d1=[]
cd_d0=[]
cm_m2=[]
cm_m1=[]
cm_m0=[]

airfoil_names=[]


for cellObj in sheet.columns[0]:
	airfoil_names.append(cellObj.value)
	
for cellObj in sheet.columns[1]:
	slopes.append(cellObj.value)

for cellObj in sheet.columns[2]:
	intercepts.append(cellObj.value)

sheet = wb.get_sheet_by_name('cd_slopes')


for cellObj in sheet.columns[1]:
        cd_d2.append(cellObj.value)
	
for cellObj in sheet.columns[2]:
	cd_d1.append(cellObj.value)

for cellObj in sheet.columns[3]:
	cd_d0.append(cellObj.value)

sheet = wb.get_sheet_by_name('cm_slopes')


for cellObj in sheet.columns[1]:
        cm_m2.append(cellObj.value)
	
for cellObj in sheet.columns[2]:
	cm_m1.append(cellObj.value)

for cellObj in sheet.columns[3]:
	cm_m0.append(cellObj.value)



#[b c taper alpha AF]
def fitness(pop):
    #Aliases        
    b_pop=pop[0]
    c_pop=pop[1]
    taper=pop[2]
    alpha_pop=pop[3]
    AF_pop=pop[4]
    d2=cd_d2[int(AF_pop)]
    d1=cd_d1[int(AF_pop)]
    d0=cd_d0[int(AF_pop)]
    m2=cm_m2[int(AF_pop)]
    m1=cm_m1[int(AF_pop)]
    m0=cm_m0[int(AF_pop)]

    #Wing Dimensions
    MAC=(2/3)*c_pop*((taper**2 + taper +1)/(taper+1))
    wing_area=b_pop*MAC
    AR=(b_pop**2)/wing_area

    #Slope Correction    
    a_new=slopes[int(AF_pop)]/(pi*e1*AR)
    a_new=slopes[int(AF_pop)]/(1+(57.3*a_new))

    #Lift Calculation
    cl=intercepts[int(AF_pop)]+(a_new*alpha_pop)
    lift=0.5*rho*(v**2)*wing_area*cl

    #Drag Calculation
    cd_i=(cl**2)/(pi*e*AR)
    cd_p=d2*(alpha_pop)**2 + d1*(alpha_pop) + d0                                                      
    cd=cd_p+cd_i
    drag=0.5*rho*(v**2)*wing_area*cd

    #Moment Calculation
    #cm=m2*(alpha_pop)**2 + m1*(alpha_pop) + m0

    #Fitness Value Calculations                                                         #Play around with Lift_fit parameters for convergence
    lift_fit=70*math.exp(-((lift-lift_const)**2)/(2*7**2))   #70,7                         #Gaussian function centered around lift_constant, A controls height
    fit=(1/cd)/50 +lift_fit #+ (1/b_pop)*5                                                        #stall angle characteristics  Minimize moment


    return fit
                            
def final_fitness(pop):
    b_pop=pop[0]
    c_pop=pop[1]
    taper=pop[2]
    alpha_pop=pop[3]
    AF_pop=int(pop[4])

    MAC=(2/3)*c_pop*((taper**2 + taper +1)/(taper+1))
    wing_area=b_pop*MAC
    AR=(b_pop**2)/wing_area
    a_new=slopes[int(AF_pop)]/(pi*e1*AR)
    a_new=slopes[int(AF_pop)]/(1+(57.3*a_new))
    cl=intercepts[int(AF_pop)]+(a_new*alpha_pop)
    cd_i=(cl**2)/(pi*e*AR)
    d2=cd_d2[int(AF_pop)]
    d1=cd_d1[int(AF_pop)]
    d0=cd_d0[int(AF_pop)]
    cd_p=d2*(alpha_pop)**2 + d1*(alpha_pop) + d0
    drag=cd_p+cd_i
    lift=0.5*rho*(v**2)*wing_area*cl
    print("AR: "+str(AR))
    print("Lift(kgs): "+str(lift/9.8))
    print("CL: "+str(cl))
    print("CD: "+str(drag))
    
    





#First Generation Initialization
b =np.random.choice(np.arange(b_const[0],b_const[1],step=0.01),size=(params[0],1),replace=True)
c =np.random.choice(np.arange(c_const[0],c_const[1],step=0.01),size=(params[0],1),replace=True)
taper =np.random.choice(np.arange(taper_const[0],taper_const[1],step=0.01),size=(params[0],1),replace=True)
alpha =np.random.choice(np.arange(alpha_const[0],alpha_const[1],step=0.5),size=(params[0],1),replace=True)
airfoil =np.random.choice(np.arange(airfoil_const[0],airfoil_const[1],step=1),size=(params[0],1),replace=True)
curPop=np.concatenate((b,c,taper,alpha,airfoil),1)
nextPop = np.zeros((curPop.shape[0], curPop.shape[1]))
fitVec = np.zeros((params[0], 2))
best_fit_overall=-np.inf


#Looping over Generations


for j in range (params[2]):
        for i in range(params[0]):
                             fitVec[i,0]=i
                             fitVec[i,1]=fitness(np.array([curPop[i,0],curPop[i,1],curPop[i,2],curPop[i,3],curPop[i,4]]))           #Needs Change

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

        #Hall of Fame
        for n in range(len(winners)):
                             selected = np.random.choice(range(len(fitVec)), params[4]/2, replace=False)
                             wnr = np.argmax(fitVec[selected,1])
                             winners[n] = curPop[int(fitVec[selected[wnr]][0])]


        nextPop[:len(winners)] = winners

        #Crossover
        nextPop[len(winners):] = np.array([np.array(np.random.permutation(np.repeat(winners[:, x], ((params[0] - len(winners))/len(winners)), axis=0))) for x in range(winners.shape[1])]).T

        #Mutation
        curPop = np.multiply(nextPop, np.matrix([np.float(np.random.uniform(0.5,1.5)) if random.random() < params[1] else 1 for x in range(nextPop.size)]).reshape(nextPop.shape))



        #Ensure all values are within constraints
        for k in range(params[0]):
                            curPop[k,4]=math.floor(math.fabs(curPop[k,4]))
                            if curPop[k,4]>airfoil_const[1]:
                                    curPop[k,4]=random.randint(0,airfoil_const[1])
                            if curPop[k,3]>alpha_const[1] or curPop[k,2]<alpha_const[0]:
                                    curPop[k,3]=np.random.uniform(alpha_const[0],alpha_const[1])
                            if curPop[k,1]>c_const[1] or curPop[k,1]<c_const[0]:
                                    curPop[k,1]=np.random.uniform(c_const[0],c_const[1])
                            if curPop[k,0]>b_const[1] or curPop[k,0]<b_const[0]:
                                    curPop[k,0]=np.random.uniform(b_const[0],b_const[1])
                            if curPop[k,2]>taper_const[1] or curPop[k,2]<taper_const[0]:
                                    curPop[k,2]=np.random.uniform(taper_const[0],taper_const[1])

                                       


print("Best Sol'n:\n%s" % (best_soln))
print("Airfoil: "+airfoil_names[int(best_soln[0,4])])
final_fitness(np.array([best_soln[0,0],best_soln[0,1],best_soln[0,2],best_soln[0,3],best_soln[0,4]]))
