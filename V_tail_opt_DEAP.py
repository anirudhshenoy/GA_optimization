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

b_const=[0.25,1.2]
c_const=[0.1,0.4]
taper_const=[0.5,0.95]
l_t_const=[0.5  ,1.2]             #From CG to C/4_t
i_t_const=[-1,+1]                 #Tail setting angle
h_cg_const=[0,0.25]
taper_const=[0.5,0.95]
E_0=4                         #Downwash angle   3.5
dE_dA=0                       #Downwash slope 



CM_ac_wb=-0.245
CM_cg_const=0.00
drag_const=0
h_ac_w=0.25                    #Added for consistency
c_wing=0.321
b_wing=1.8
S_wing=c_wing*b_wing
wing_airfoil=504
alpha_wing=3


rho=1.227
V_vt=0.07
v=12
e1=0.95
e=0.9
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
cl_wing=a_wing*alpha_wing + intercepts[int(wing_airfoil)]


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
toolbox.register("attr_h_cg", random.uniform, h_cg_const[0],h_cg_const[1])



N_CYCLES=1
toolbox.register("individual", tools.initCycle, creator.Individual,
                 (toolbox.attr_span, toolbox.attr_chord,toolbox.attr_i_t,toolbox.attr_airfoil,toolbox.attr_l_t, toolbox.attr_taper, toolbox.attr_h_cg), n=N_CYCLES)

toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evalOneMax(individual):
    #print (individual)
    #Aliases        
    b_pop=individual[0]                     #CHECK THIS ON NEXT RUN
    c_pop=individual[1]
    i_pop=individual[2]
    AF_pop=individual[3]
    l_pop=individual[4]
    taper=individual[5]
    h_cg=individual[6]
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
    cl=a_new*alpha_wing*(1-dE_dA)-(a_new*(i_pop+E_0))+intercepts[int(AF_pop)]
    #cl=cl*math.cos(35/57.29)
    

    #Drag Calculation
    cd_i=(cl**2)/(pi*e*AR)
    cd_p=d2*(alpha_wing-(i_pop+E_0))**2 + d1*(alpha_wing-(i_pop+E_0)) + d0
    cd=cd_i+cd_p
    drag=0.5*rho*(v**2)*tail_area*cd
    
    V_h=(l_pop*tail_area*(math.cos(35/57.29)**2))/(S_wing*c_wing)

    CM_cg=CM_ac_wb-(V_h*cl)#s+cl_wing*(h_cg-h_ac_w)

    #Fitness Value Calculations                                                         #Play around with Lift_fit parameters for convergence
    cm_fit=100*math.exp(-(((CM_cg-CM_cg_const)*100)**2)/(2*100**2))                            #Gaussian function centered around lift_constant, A controls height
    drag_fit=10*math.exp(-((drag-drag_const)**2)/(2*35**2))
    fit=cm_fit +drag_fit

    return (fit,)

def calculate_vtail(specs):
    h_span=specs[0][0]
    h_chord=specs[0][1]
    h_i=specs[0][2]
    h_af=specs[0][3]
    h_l=specs[0][4]
    h_taper=specs[0][5]
    h_cg=specs[0][6]

    #Wing Dimensions
    MAC=(2/3)*h_chord*((h_taper**2 + h_taper +1)/(h_taper+1))
    
    tail_area=h_span*MAC
    #print(c_pop)
    AR=(h_span**2)/tail_area

    #Slope Correction    
    a_new=slopes[int(h_af)]/(pi*e1*AR)
    a_new=slopes[int(h_af)]/(1+(57.3*a_new))

    #Lift Calculation
    cl=a_new*alpha_wing*(1-dE_dA)-(a_new*(h_i+E_0))+intercepts[int(h_af)]
    #cl=cl*math.cos(35/57.29)

    V_h=(h_l*tail_area*(math.cos(35/57.29)**2))/(S_wing*c_wing)

    CM_cg=CM_ac_wb-(V_h*cl)#+cl_wing*(h_cg-h_ac_w)
    

    print("H Span: " +str(h_span))
    print("H Chord: "+ str(h_chord))
    print("H Incidence Angle: "+ str(h_i))
    print("H Airfoil: "+ airfoil_names[int(h_af)])
    print("H Tip Chord: "+str(h_taper*h_chord))
    print("Moment Arm: "+str(h_l))
    print("M_cg: " +str(CM_cg))

    h_area=h_span*h_chord
    #v_area=(b_wing*b_wing*c_wing*V_vt)/h_l
    v_area=math.atan(35/57.29)*h_area
    #d_angle=math.atan(v_area/h_area)
    print("V Tail Area: "+ str(h_area+v_area))
    #print("V Tail Angle: "+str(d_angle*57.29))
    
    

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
                            if curPop[6]>h_cg_const[1] or curPop[6]<h_cg_const[0]:
                                    curPop[6]=numpy.random.uniform(h_cg_const[0],h_cg_const[1])


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
    
    
    pop = toolbox.population(n=300)
    #print(pop)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)
    
    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.8, halloffame=hof, mutpb=0.05, ngen=40,stats=stats, verbose=True)
    print (hof)
    calculate_vtail(hof)
    
    return pop, log, hof

if __name__ == "__main__":
    main()
