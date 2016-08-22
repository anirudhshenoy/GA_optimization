import csv
import os
import numpy as np
import h5py

databaseFileName='airfoil_data_xml.xml'
flat=1
generated=1
tail=0
symmetric=0

airfoil_no=1
angles=np.arange(-5,12.5,0.5)
ids=list(range(2,len(angles)+2))
angle_keys=dict(zip(angles,ids))


airfoil_descriptor=[flat,generated,tail,symmetric]

#Airfoil Descriptor is a list with 1=Yes and 0=No [Flat, Generated, Tail, Symmetric]
def h5py_writer(airfoil_id, airfoil_name, airfoil_descriptor, cl_xml,cd_xml, x_coords,y_coords):
    with h5py.File('airfoil_data.h5', 'a') as hf:
        airfoil_grp=hf.create_group('airfoil_id_'+str(airfoil_id))
        #cl_grp = hf.create_group('airfoil_id_'+str(airfoil_id)+'/cl')
        airfoil_grp.create_dataset('cl', data = cl_xml, compression="gzip", compression_opts=9)
        #cd_grp = hf.create_group('airfoil_id_'+str(airfoil_id)+'/cd')
        airfoil_grp.create_dataset('cd', data = cd_xml, compression="gzip", compression_opts=9)
        #x_coords_grp=hf.create_group('airfoil_id_'+str(airfoil_id)+'/coords/x_coords')
        airfoil_grp.create_dataset('x_coords', data = x_coords, compression="gzip", compression_opts=9)
        #y_coords_grp=hf.create_group('airfoil_id_'+str(airfoil_id)+'/coords/y_coords')
        airfoil_grp.create_dataset('y_coords', data = y_coords, compression="gzip", compression_opts=9)
        airfoil_grp.create_dataset('name', data=airfoil_name)
        airfoil_grp.create_dataset('descriptor', data=airfoil_descriptor)
        
        
    




def reject_outliers(data, m = 2.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    return s<m



os.chdir('C:\\Users\Aniru_000\Desktop\TD-1\Airfoil\s1223\\airfoil\\MasterPolarsFlat\\')
#start Airfoil Loop Here
for file in os.listdir(os.getcwd()):
    if file.endswith(".txt"):
        print('Parsing File:'+file+"   Airfoil No:"+str(airfoil_no))
        
        with open(file, newline='') as f:

            csv_f=csv.reader(f)
            rowNum=0
            alpha=[]
            cl=[]
            cd=[]
            cdp=[]
            cm=[]
            top_xtr=[]
            bot_xtr=[]
            for row in csv_f:
                
                if rowNum==2:           
                    airfoil=str(row)
                    
                    airfoil=airfoil.split(':')
                    print(airfoil)
                    #airfoil_1=airfoil[1].split(' ')[1]
                    airfoil=airfoil[1][:-2]
                    print("Airfoil Name: "+airfoil)
                if rowNum>=11:
                    
                    rowData=str(row)
                    rowData=rowData.split()
                    if len(rowData)>1:
                        alpha.append(float(rowData[1]))
                        cl.append(float(rowData[2]))
                        cd.append(float(rowData[3]))
                        cdp.append(float(rowData[4]))
                        cm.append(float(rowData[5]))
                        top_xtr.append(float(rowData[6]))
                        bot_xtr.append(float(rowData[7][0:6]))
                    
                rowNum+=1

            

            

            if len(alpha)>10:
                in_index=reject_outliers(cd)
                cd=[cd[i-1] for i, elem in enumerate(in_index, 1) if elem]
                alpha=[alpha[i-1] for i, elem in enumerate(in_index, 1) if elem]
                cl=[cl[i-1] for i, elem in enumerate(in_index, 1) if elem]
                cdp=[cdp[i-1] for i, elem in enumerate(in_index, 1) if elem]
                top_xtr=[top_xtr[i-1] for i, elem in enumerate(in_index, 1) if elem]
                bot_xtr=[bot_xtr[i-1] for i, elem in enumerate(in_index, 1) if elem]
                cm=[cm[i-1] for i, elem in enumerate(in_index, 1) if elem]
                
                cl_xml=np.polyfit(alpha,cl,1)
                
                cd_xml=np.polyfit(alpha,cd,2)               #Add outlier rejection
        
                
                
            


                #Write to XLS     
             
                for filename in os.listdir('C:\\Users\Aniru_000\Desktop\TD-1\Airfoil\s1223\\airfoil\\MasterPolarsFlat\\Flat_airfoils_dat\\'):
                    if filename==(airfoil[1:] + '.dat'):

                        with open( 'C:\\Users\Aniru_000\Desktop\TD-1\Airfoil\s1223\\airfoil\\MasterPolarsFlat\\Flat_airfoils_dat\\'+ filename, newline='', encoding='utf8') as fo:


                            csv_fo=csv.reader(fo)
                            rowNum=0
                            x_coord_xml=[]
                            y_coord_xml=[]
                            for row in csv_fo:

                                if rowNum>=1:
                                    rowData=str(row)
                                    
                                    rowData=rowData[2:-2].split()
                                    
                                    x_coord_xml.append(float(rowData[0]))
                                    y_coord_xml.append(float(rowData[1]))
                                    
                                    
                                rowNum+=1

                         
                    
            h5py_writer(airfoil_no,airfoil,airfoil_descriptor,cl_xml,cd_xml,x_coord_xml,y_coord_xml) 
            airfoil_no+=1
    #if airfoil_no==1:
    #    exit()


        
 


