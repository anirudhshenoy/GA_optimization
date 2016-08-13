import random
import numpy
import math

import openpyxl
from openpyxl.styles import Alignment
from openpyxl import Workbook

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

b_const=[0.5,2.25]
c_const=[0.2,0.4]
taper_const=[0.5,0.95]
alpha_const=[0,3]


AR_const=5
lift_const=43
drag_const=0
area_const=1
rho=1.227
v=10
e1=0.9
e=0.85
pi=3.1415

wb = openpyxl.load_workbook('C:/Users/Aniru_000/Desktop/TD-1/Airfoil/s1223/airfoil/MasterPolarsFlat/airfoilpolars_master.xlsx')
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
airfoil_const=[0,len(slopes)-1]


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







creator.create("FitnessMax", base.Fitness,weights=(1.0,1.0,1.0 ,1.0,))
creator.create("Individual", list,typecode='i', fitness=creator.FitnessMax)

IND_SIZE=5


toolbox = base.Toolbox()
toolbox.register("attr_span", random.uniform, b_const[0], b_const[1])
toolbox.register("attr_chord", random.uniform, c_const[0], c_const[1])
toolbox.register("attr_taper", random.uniform, taper_const[0],taper_const[1])
toolbox.register("attr_alpha", random.uniform, alpha_const[0],alpha_const[1])
toolbox.register("attr_airfoil", random.randint, airfoil_const[0],airfoil_const[1])

N_CYCLES=1
toolbox.register("individual", tools.initCycle, creator.Individual,
                 (toolbox.attr_span, toolbox.attr_chord, toolbox.attr_taper, toolbox.attr_alpha,toolbox.attr_airfoil), n=N_CYCLES)

toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evalOneMax(individual):
    #print (individual)
    #Aliases        
    b_pop=individual[0]
    c_pop=individual[1]
    taper=individual[2]
    alpha_pop=individual[3]
    AF_pop=individual[4]
    d2=cd_d2[int(AF_pop)]
    d1=cd_d1[int(AF_pop)]
    d0=cd_d0[int(AF_pop)]
    m2=cm_m2[int(AF_pop)]
    m1=cm_m1[int(AF_pop)]
    m0=cm_m0[int(AF_pop)]

    #Wing Dimensions
    MAC=(2/3)*c_pop*((taper**2 + taper +1)/(taper+1))
    
    wing_area=b_pop*MAC
    #print(c_pop)
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
    lift_fit=70*math.exp(-((lift-lift_const)**2)/(2*35**2))   #70,7                         #Gaussian function centered around lift_constant, A controls height
    drag_fit=70*math.exp(-((drag-drag_const)**2)/(2*35**2))
    #fit=(1/cd)/50 +lift_fit #+ (1/b_pop)*5                                                        #stall angle characteristics  Minimize moment
    fit=lift_fit+drag_fit+ (1/b_pop)*5  

    return (fit,)

def checkBounds(min, max):
    def decorator(func):
        def wrapper(*args, **kargs):
            offspring = func(*args, **kargs)
            for curPop in offspring:
                            curPop[4]=math.floor(math.fabs(curPop[4]))
                            if curPop[4]>airfoil_const[1]:
                                    curPop[4]=random.randint(0,airfoil_const[1])
                            if curPop[3]>alpha_const[1] or curPop[3]<alpha_const[0]:
                                    curPop[3]=numpy.random.uniform(alpha_const[0],alpha_const[1])
                            if curPop[1]>c_const[1] or curPop[1]<c_const[0]:
                                    curPop[1]=numpy.random.uniform(c_const[0],c_const[1])
                            if curPop[0]>b_const[1] or curPop[0]<b_const[0]:
                                    curPop[0]=numpy.random.uniform(b_const[0],b_const[1])
                            if curPop[2]>taper_const[1] or curPop[2]<taper_const[0]:
                                    curPop[2]=numpy.random.uniform(taper_const[0],taper_const[1])

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
    random.seed(64)
    
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
