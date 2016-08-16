import random
import numpy
import math
import multiprocessing



import openpyxl
from openpyxl.styles import Alignment
from openpyxl import Workbook

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

b_const=[0.25,1]
c_const=[0.2,0.3]
taper_const=[0.5,0.95]
l_t_const=[0.6,1.0]             #From CG to C/4_t
i_t_const=[-10,+10]                 #Tail setting angle
taper_const=[0.5,0.95]
E_0=3                         #Downwash angle   3.5
dE_dA=0.1                       #Downwash slope 



CM_ac_wb=-0.245
CM_cg_const=0.01
h_h_ac_w=0                    #Added for consistency
c_wing=0.321
b_wing=1.8
S_wing=c_wing*b_wing
wing_airfoil=504
alpha_wing=3


rho=1.227
v=10
e1=0.9
e=0.85
pi=3.1415

wb = openpyxl.load_workbook('C:/Users/Aniru_000/Desktop/TD-1/Airfoil/s1223/airfoil/MasterPolarsFlat/airfoilpolars_master.xlsx')
wb2 = openpyxl.load_workbook('C:/Users/Aniru_000/Desktop/TD-1/Airfoil/s1223/airfoil/tail_foil_naca/Inverted/Polars/airfoilpolars_master.xlsx')
print ("Opened File")
sheet = wb.get_sheet_by_name('slopes')                #Change to index based
print ("Opened Sheet")
slopes=[]
intercepts=[]
a_0=[]
cd_d2=[]
cd_d1=[]
cd_d0=[]


airfoil_names=[]


	
for cellObj in sheet.columns[1]:
	slopes.append(cellObj.value)

for cellObj in sheet.columns[2]:
	intercepts.append(cellObj.value)

AR=(b_wing**2)/S_wing
a_wing=slopes[int(wing_airfoil)]/(pi*e1*AR)
a_wing=slopes[int(wing_airfoil)]/(1+(57.3*a_wing))

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

sheet = wb2.get_sheet_by_name('cd_slopes')


for cellObj in sheet.columns[1]:
        cd_d2.append(cellObj.value)
	
for cellObj in sheet.columns[2]:
	cd_d1.append(cellObj.value)

for cellObj in sheet.columns[3]:
	cd_d0.append(cellObj.value)

airfoil_const=[0,len(slopes)-1]


creator.create("FitnessMax", base.Fitness,weights=(1.0,1.0,1.0 ,1.0,))
creator.create("Individual", list,typecode='i', fitness=creator.FitnessMax)

IND_SIZE=6


toolbox = base.Toolbox()

toolbox.register("attr_span", random.uniform, b_const[0], b_const[1])
toolbox.register("attr_chord", random.uniform, c_const[0], c_const[1])
toolbox.register("attr_taper", random.uniform, taper_const[0],taper_const[1])
toolbox.register("attr_i_t", random.uniform, i_t_const[0],i_t_const[1])
toolbox.register("attr_l_t", random.uniform, l_t_const[0],l_t_const[1])
toolbox.register("attr_airfoil", random.randint, airfoil_const[0],airfoil_const[1])

N_CYCLES=1
toolbox.register("individual", tools.initCycle, creator.Individual,
                 (toolbox.attr_span, toolbox.attr_chord,toolbox.attr_i_t,toolbox.attr_airfoil,toolbox.attr_l_t, toolbox.attr_taper), n=N_CYCLES)

toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evalOneMax(individual):
    #print (individual)
    #Aliases        
    b_pop=individual[0]
    c_pop=individual[1]
    i_pop=individual[2]
    AF_pop=individual[3]
    l_pop=individual[4]
    taper=individual[5]
    d2=cd_d2[int(AF_pop)]
    d1=cd_d1[int(AF_pop)]
    d0=cd_d0[int(AF_pop)]
   
    #Wing Dimensions
    MAC=(2/3)*c_pop*((taper**2 + taper +1)/(taper+1))
    
    tail_area=b_pop*MAC
    #print(c_pop)
    AR=(b_pop**2)/tail_area

    #Slope Correction    
    a_new=slopes[int(AF_pop)]/(pi*e1*AR)
    a_new=slopes[int(AF_pop)]/(1+(57.3*a_new))

    #Lift Calculation
    cl=a_new*alpha_wing*(1-dE_dA)-(a_new*(i_pop+E_0))
    

    #Drag Calculation
    cd_i=(cl**2)/(pi*e*AR)
    cd_p=d2*(alpha_wing-(i_pop+E_0))**2 + d1*(alpha_wing-(i_pop+E_0)) + d0
    cd=cd_i+cd_p
    
    V_h=(l_pop*tail_area)/(S_wing*c_wing)

    CM_cg=CM_ac_wb-(V_h*cl)

    #Fitness Value Calculations                                                         #Play around with Lift_fit parameters for convergence
    cm_fit=100*math.exp(-(((CM_cg-CM_cg_const)*1000)**2)/(2*1000**2))                            #Gaussian function centered around lift_constant, A controls height
    fit=cm_fit +math.fabs(1/cd)/10 #+(1/c_pop)*2 

    return (fit,)

def checkBounds(min, max):
    def decorator(func):
        def wrapper(*args, **kargs):
            offspring = func(*args, **kargs)
            for curPop in offspring:
                            curPop[3]=math.floor(math.fabs(curPop[3]))
                            if curPop[3]>airfoil_const[1]:
                                    curPop[3]=random.randint(0,airfoil_const[1])
                            if curPop[2]>i_t_const[1] or curPop[2]<i_t_const[0]:
                                    curPop[2]=numpy.random.uniform(i_t_const[0],i_t_const[1])
                            if curPop[1]>c_const[1] or curPop[1]<c_const[0]:
                                    curPop[1]=numpy.random.uniform(c_const[0],c_const[1])
                            if curPop[0]>b_const[1] or curPop[0]<b_const[0]:
                                    curPop[0]=numpy.random.uniform(b_const[0],b_const[1])
                            if curPop[5]>taper_const[1] or curPop[5]<taper_const[0]:
                                    curPop[5]=numpy.random.uniform(taper_const[0],taper_const[1])
                            if curPop[4]>l_t_const[1] or curPop[4]<l_t_const[0]:
                                    curPop[4]=numpy.random.uniform(l_t_const[0],l_t_const[1])

            return offspring
        return wrapper
    return decorator               

toolbox.register("evaluate", evalOneMax)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutGaussian, mu=1.0, sigma=0.2, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

toolbox.decorate("mate", checkBounds(0, 1))
toolbox.decorate("mutate", checkBounds(0, 1))

def main():
    #random.seed(64)
    
    pop = toolbox.population(n=300)
    #print(pop)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)
    
    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.8, halloffame=hof, mutpb=0.05, ngen=40,stats=stats, verbose=True)
    
    print(hof)
    return pop, log, hof

if __name__ == "__main__":
    main()
