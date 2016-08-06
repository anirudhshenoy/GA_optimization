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

params = [500, 0.15, 250, 4, 100]
#plt.axis([0, 260, 0, 2.6])
#plt.ion()
#These are just some parameters for the GA, defined below in order:
# [Init pop (pop=100), mut rate (=5%), num generations (250), chromosome/solution length (3), # winners/per gen]

b_const=[0.1,2.5]
c_const=[0.1,0.4]
alpha_const=[0,3]
airfoil_const=[0,639]          #1468 for General AFs
AR_const=5
lift_const=40
area_const=1
rho=1.227
v=10
e1=0.85
e=0.85
pi=3.1415

#curPop=np.empty([params[0],params[3]])


#root=tk.Tk()
#root.withdraw()
#file_path=filedialog.askopenfilename()
#print(file_path)

wb = openpyxl.load_workbook('C:/Users/Aniru_000/Desktop/TD-1/Airfoil/s1223/airfoil/MasterPolarsFlat/airfoilpolars_master.xlsx')
print ("Opened File")
sheet = wb.get_sheet_by_name('slopes')                #Change to index based
print ("Opened Sheet")
slopes=[]
intercepts=[]
cd_d0=[]
cd_d1=[]                                        #Please fix this shit
cd_d2=[]
airfoil_names=[]


for cellObj in sheet.columns[0]:
	airfoil_names.append(cellObj.value)
	
for cellObj in sheet.columns[1]:
	slopes.append(cellObj.value)

for cellObj in sheet.columns[2]:
	intercepts.append(cellObj.value)

sheet = wb.get_sheet_by_name('slopes1')

for cellObj in sheet.columns[1]:
	cd_d2.append(cellObj.value)
	
for cellObj in sheet.columns[2]:
	cd_d1.append(cellObj.value)

for cellObj in sheet.columns[3]:
	cd_d0.append(cellObj.value)


#[b c alpha AF]
def fitness(pop):
    b_pop=pop[0]
    c_pop=pop[1]
    alpha_pop=pop[2]
    AF_pop=pop[3]
    wing_area=b_pop*c_pop
    AR=(b_pop**2)/wing_area
    a_new=slopes[int(AF_pop)]/(pi*e1*AR)
    a_new=slopes[int(AF_pop)]/(1+(57.3*a_new))
    cl=intercepts[int(AF_pop)]+(a_new*alpha_pop)
    cd_i=(cl**2)/(pi*e*AR)
    d2=cd_d2[int(AF_pop)]
    d1=cd_d1[int(AF_pop)]
    d0=cd_d0[int(AF_pop)]

    cd_p=d2*(alpha_pop)**2 + d1*(alpha_pop) + d0
    lift=0.5*rho*(v**2)*wing_area*cl                    #Add intercept to lift slope predictor
    cd=cd_p+cd_i
    drag=0.5*rho*(v**2)*wing_area*cd    
    if AR>=AR_const and wing_area<=area_const and lift>= lift_const and (b_pop>=b_const[0] and b_pop<=b_const[1]) and (c_pop>=c_const[0] and c_pop<=c_const[1]) and (alpha_pop>=alpha_const[0] and alpha_pop<=alpha_const[1]):
            #Lift
            #AR
            #wing_area
            #
            #fit=(4/((pop[1]**2)*pop[0])) + (1/drag)                 #Added Alpha +lift/3 
            fit=(lift/drag) +AR                     #stall angle characteristics  Minimize moment
    else:
            fit=-np.inf                         #Replacing this with a fitness function causes problems because b,c for some reason have huge values after Gen1 ? Because of Mutation ?
                                                #Replacing with a function instead would alow the program to know how bad the individual was, might allow for faster convergence 
    return fit
                            
def final_fitness(pop):
    b_pop=pop[0]
    c_pop=pop[1]
    alpha_pop=pop[2]
    AF_pop=int(pop[3])
    wing_area=b_pop*c_pop
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
    
    

b =np.random.choice(np.arange(b_const[0],b_const[1],step=0.01),size=(params[0],1),replace=True)
c =np.random.choice(np.arange(c_const[0],c_const[1],step=0.01),size=(params[0],1),replace=True)
alpha =np.random.choice(np.arange(alpha_const[0],alpha_const[1],step=0.5),size=(params[0],1),replace=True)
airfoil =np.random.choice(np.arange(airfoil_const[0],airfoil_const[1],step=1),size=(params[0],1),replace=True)


#Implement Constraints as part of fitness function



curPop=np.concatenate((b,c,alpha,airfoil),1)
nextPop = np.zeros((curPop.shape[0], curPop.shape[1]))
fitVec = np.zeros((params[0], 2))
best_fit_overall=0

for j in range (params[2]):
        for i in range(params[0]):
                             fitVec[i,0]=i
                             fitVec[i,1]=fitness(np.array([curPop[i,0],curPop[i,1],curPop[i,2],curPop[i,3]]))

        winners = np.zeros((params[4], params[3]))
        best_fit=max(fitVec[:,1])
        best_cand=np.argmax(fitVec[:,1])
        if best_fit>best_fit_overall:
               best_soln = curPop[np.argmax(fitVec[:,1])]
               best_b=best_soln[0]
               best_fit_overall=best_fit
               
        print("(Gen: #%s) Best Fitness: %s" % (j,best_fit))
        print("Airfoil: "+ airfoil_names[int(curPop[best_cand,3])])
        for n in range(len(winners)):
                             selected = np.random.choice(range(len(fitVec)), params[4]/2, replace=False)
                             wnr = np.argmax(fitVec[selected,1])
                             winners[n] = curPop[int(fitVec[selected[wnr]][0])]


        nextPop[:len(winners)] = winners
        nextPop[len(winners):] = np.array([np.array(np.random.permutation(np.repeat(winners[:, x], ((params[0] - len(winners))/len(winners)), axis=0))) for x in range(winners.shape[1])]).T
        curPop = np.multiply(nextPop, np.matrix([np.float(np.random.normal(0,2,1)) if random.random() < params[1] else 1 for x in range(nextPop.size)]).reshape(nextPop.shape))
        for k in range(params[0]):
                            curPop[k,3]=math.floor(math.fabs(curPop[k,3]))
                            if curPop[k,3]>airfoil_const[1]:
                                    curPop[k,3]=random.randint(0,airfoil_const[1])

        #plt.scatter(j, best_b)
        #plt.pause(0.005)

                            


print("Best Sol'n:\n%s" % (best_soln))
print("Airfoil: "+airfoil_names[int(best_soln[0,3])])
final_fitness(np.array([best_soln[0,0],best_soln[0,1],best_soln[0,2],best_soln[0,3]]))

#while True:
#    plt.pause(0.001)
