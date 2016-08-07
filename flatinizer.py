import csv
import os
import math
airfoil_no=1
os.chdir('C:\\Users\Aniru_000\Desktop\TD-1\Airfoil\s1223\\airfoil\Completed') #
#start Airfoil Loop Here
for file in os.listdir(os.getcwd()):
    if file.endswith(".dat"):
        print('Parsing File:'+file+"   Airfoil No:"+str(airfoil_no))
        
        with open(file, newline='', encoding='utf8') as f:

            csv_f=csv.reader(f)
            rowNum=0
            x_coord=[]
            y_coord=[]
            cd=[]
            cdp=[]
            cm=[]
            top_xtr=[]
            bot_xtr=[]
            for row in csv_f:
                if rowNum==0:
                    airfoil=str(row)
                #    airfoil=airfoil.split(':')
                #    airfoil_1=airfoil[1].split(' ')[1]
                #    airfoil=airfoil_1+" "+airfoil[1].split(' ')[2]
                #    print("Airfoil Name: "+airfoil)
                if rowNum>=1:
                    rowData=str(row)
                    
                    rowData=rowData[2:-2].split()
                    
                    #if len(rowData)>2:
                    #    x_coord.append(float(rowData[1]))
                    #    y_coord.append(float(rowData[2][:-2]))
                    #else:
                    x_coord.append(float(rowData[0]))
                    y_coord.append(float(rowData[1]))
                    
                    #alpha.append(float(rowData[1]))
                    #cl.append(float(rowData[2]))
                    #cd.append(float(rowData[3]))
                    #cdp.append(float(rowData[4]))
                    #cm.append(float(rowData[5]))
                    #top_xtr.append(float(rowData[6]))
                    #bot_xtr.append(float(rowData[7][0:6]))
                    
                rowNum+=1
            for i in range(math.floor(len(x_coord)/2),len(x_coord)):
                        y_coord[i]=0

            outputFile = open('Flat_bot\\' + file[:-4]+'_flat.dat', 'w', newline='')
            outputWriter = csv.writer(outputFile, delimiter='\t')
            outputWriter.writerow([airfoil[2:-2]])
            for i in range(len(x_coord)):
                outputWriter.writerow([x_coord[i],y_coord[i]])
            outputFile.close()
    airfoil_no+=1
            
