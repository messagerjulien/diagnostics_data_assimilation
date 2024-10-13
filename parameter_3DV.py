###
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DayLocator, HourLocator
from matplotlib.ticker import (MultipleLocator,
                               FormatStrFormatter,
                               AutoMinorLocator)
import numpy as np
import os
import pandas as pd
import re
#########################################
years = ['2024']
months = ['06']
#days = ['15', '16', '17', '18']
days = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16','17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31',]
cycles = ['12']
#cycles = ['00','03','06','09','12','15','18', '21']
path = '/scratch/nld5621/logFilesnoModeS'
path1 = '/scratch/nld5621/logFilesModeS'
out_path = '/scratch/nld5621/logFilesnoModeS/JOstatistics'
out_path1 = '/scratch/nld5621/logFilesModeS/JOstatistics'
labelplot = 'development'
keep_JOtables = True
figs = True

#Specific humidity
Variables = ['Q', 'RAD', 'RAD']
Obstypes = ['Radiosondes', 'MHS', 'ATMS']

#Wind
#Variables = ['U', 'U']
#Obstypes = ['Aircraft', 'Radiosondes']

#Temperature
#Variables = ['T', 'T', 'RAD']
#Obstypes =  ['Aircraft', 'Radiosondes', 'AMSUA']

#################################
def main ():
    
    print (">>>> Diagnostics using cost function information from log files <<<<<")

# Sanity checks
    #if (np.size(Codetype) == 0 or  np.size(Variable) == 0):
    #    print ("ERROR: check your settings for Codetype and Variable")
    #    print("Codetype: ", Codetype)
    #    print("Variable : ", Variable)
    #    exit()
    

    
    JoCTydf = []


    JoGlobalAll = []
    JoCtypeall1 = []
    date_dfAll = []

    for year in years:
        for month in months :
            for day in days:
                for cy in cycles:
                    try :
                        d = datetime.datetime(int(year),int(month),
                                                            int(day),int(cy)).strftime("%Y-%m-%d %H")
                        fileLog = '{}/HM_Date_{}{}{}{}.html'.format(path,year,month,day,cy)
                        fileJOtable = '{}/JOtable_{}{}{}{}.txt'.format(out_path,year,month,day,cy)
                        if not os.path.isfile(fileLog):
                            raise FileNotFoundError
                        Jo_total = [0, 0]
                        N_total = [0, 0]
                        for i in range(len(Variables)):
                            num_code = 0
                            Variable = Variables[i]
                            Obstype = Obstypes[i]
                            Codetype = SetCodetype(Obstype, Variable)
                            for cty in Codetype :
                                num_code = num_code + 1
                    

                                print(">>>>>>> Reading the log file in: ", fileLog)
                                #extractJOtable(fileLog, fileJOtable)
                                try :
                                    #print(">>>>>>> Reading the JoGlobal")
                                    Global = readGlobal(fileJOtable)
                                    df1 = pd.DataFrame(Global['JoGlobal'])
                                    df2 = pd.DataFrame(Global['Ntotal'])
                                    dataListG = createDataList(df1, df2)
                                    JoGlobal = pd.DataFrame(dataListG)

                                    
                                    date_df = pd.DataFrame ({"datetime": [d]} )
                                    JoGlobalAll.append(JoGlobal)
                                    

                                    print(">>>>>>> Reading the Jo{}: ".format(cty))
                                    Observations = readObservations(fileJOtable, cty, Variable)
                                    
                                    Jo_total = [Jo_total[i] + Observations['JoOBS'][0][i] for i in range(2)]
                                    N_total = [N_total[i] + Observations['NOBS'][0][i] for i in range(2)]
                                    
                                except IndexError :
                                    pass
                        date_dfAll.append(date_df)
                        print(d, "DATE INCLUSE")
                        dataListC = createDataList(Jo_total, N_total)
                        JoCTy = pd.DataFrame(dataListC)
                        print('JOCTY !!!!!!!!!!!!!!!', JoCTy)
                        JoCtypeall1.append(JoCTy)

                        if keep_JOtables is False:
                            print(">>>>>>> deleting: ", fileJOtable)
                            os.remove (fileJOtable)
                    except (IOError, ValueError, FileNotFoundError) as error :
                        pass

    print(">>>>>>> Creating the list of Jo(s)")
    JoGlobalAll = pd.concat(JoGlobalAll, ignore_index=True, axis=0)
    JoCtypeall1 = pd.concat(JoCtypeall1, ignore_index=True, axis=0)
    dateAll = pd.concat(date_dfAll, ignore_index= True, axis=0) 


    JoGlobalAll = pd.concat([dateAll, JoGlobalAll], axis=1)
    JoCtypeall1 = pd.concat([dateAll, JoCtypeall1], axis=1)

    print(">>>>>>> writing Jo(s) in :", out_path)
    Jodf = writeJoGlobal(out_path, JoGlobalAll,"Global")
    JoCTydf = writeJoGlobal(out_path, JoCtypeall1, "Observations_{}_{}".format(Obstype,num_code, Variable))
    print(">>>>>>> saving Jo(s) plots in :", out_path)

    #if (figs):  plotJo('JoCtype', out_path, JoCTydf, Obstype, num_code, cty, Variable, labelplot)

    #if (figs): plotJo('JoGlobal', out_path, Jodf,"Global","", "", "",labelplot)
    

    
    compteur = 0

    num_code = 0

    JoCTydf1 = []


    JoGlobalAll = []
    JoCtypeall1 = []
    JoCtypeAll2 = []
    date_dfAll = []

    for year in years:
        for month in months :
            for day in days:
                for cy in cycles:
                    try :
                        d = datetime.datetime(int(year),int(month),
                                                            int(day),int(cy)).strftime("%Y-%m-%d %H")
                        Jo_total = [0, 0]
                        N_total = [0, 0]
                        Jo_no147 = [0, 0]
                        N_no147 = [0, 0]
                        for i in range(len(Variables)): # 3 = number of observation types we study here
                            num_code = 0
                            Variable = Variables[i]
                            Obstype = Obstypes[i]
                            Codetype = SetCodetype(Obstype, Variable)
                            for cty in Codetype :
                                num_code = num_code + 1
                                
                                fileLog = '{}/HM_Date_{}{}{}{}.html'.format(path1,year,month,day,cy)
                                fileJOtable = '{}/JOtable_{}{}{}{}.txt'.format(out_path1,year,month,day,cy)
                                if not os.path.isfile(fileLog):
                                    raise FileNotFoundError
                                print(">>>>>>> Reading the log file in: ", fileLog)
                                #extractJOtable(fileLog, fileJOtable)
                                
                                try :
                                    #print(">>>>>>> Reading the JoGlobal")
                                    Global = readGlobal(fileJOtable)
                                    df1 = pd.DataFrame(Global['JoGlobal'])
                                    df2 = pd.DataFrame(Global['Ntotal'])
                                    dataListG = createDataList(df1, df2)
                                    JoGlobal = pd.DataFrame(dataListG)

                                    date_df = pd.DataFrame ({"datetime": [d]} )
                                    JoGlobalAll.append(JoGlobal)

                                    print(">>>>>>> Reading the Jo{}: ".format(cty))
                                    Observations = readObservations(fileJOtable, cty, Variable)
                                    if not cty == 'Codetype   147' :
                                        Jo_no147 = [Jo_no147[i] + Observations['JoOBS'][0][i] for i in range(2)]
                                        N_no147 = [N_no147[i] + Observations['NOBS'][0][i] for i in range(2)]
                                    
                                    Jo_total = [Jo_total[i] + Observations['JoOBS'][0][i] for i in range(2)]
                                    N_total = [N_total[i] + Observations['NOBS'][0][i] for i in range(2)]
                                    
                                except IndexError:
                                    pass
                        date_dfAll.append(date_df)
                        dataListC = createDataList(Jo_total, N_total)
                        dataListD = createDataList(Jo_no147, N_no147)
                        JoCTy = pd.DataFrame(dataListC)
                        JoCTy2 = pd.DataFrame(dataListD)

                        JoCtypeall1.append(JoCTy)
                        JoCtypeAll2.append(JoCTy2)
                        if keep_JOtables is False:
                            print(">>>>>>> deleting: ", fileJOtable)
                            os.remove (fileJOtable)
                    except (IOError, ValueError) as error :
                        pass

    print(">>>>>>> Creating the list of Jo(s)")
    JoGlobalAll = pd.concat(JoGlobalAll, ignore_index=True, axis=0)
    JoCtypeall1 = pd.concat(JoCtypeall1, ignore_index=True, axis=0)
    dateAll = pd.concat(date_dfAll, ignore_index= True, axis=0) 

    

    JoGlobalAll = pd.concat([dateAll, JoGlobalAll], axis=1)
    JoCtypeall1 = pd.concat([dateAll, JoCtypeall1], axis=1)

    print(">>>>>>> writing Jo(s) in :", out_path)
    Jodf = writeJoGlobal(out_path, JoGlobalAll,"Global")
    JoCTydf1 = writeJoGlobal(out_path, JoCtypeall1, "Observations_{}_{}".format(Obstype,num_code, Variable))
    print(">>>>>>> saving Jo(s) plots in :", out_path)



    JoCtypeAll2 = pd.concat(JoCtypeAll2, ignore_index=True, axis=0)
    dateAll2 = pd.concat(date_dfAll, ignore_index= True, axis=0) 

    

    JoCtypeAll2 = pd.concat([dateAll, JoCtypeAll2], axis=1)


    JoCTydf2 = writeJoGlobal(out_path, JoCtypeAll2, "Observations_{}_{}".format(Obstype,num_code, Variable))
    print(">>>>>>> saving Jo(s) plots in :", out_path)



    if (figs): plotJo('JoGlobal', out_path, JoCTydf, JoCTydf1, JoCTydf2, "Global","", "", "",labelplot)
    

#######
def SetCodetype (Obstype, Variable):

    if (Obstype == 'SYNOP') : 
        Codetype = ['Codetype    14', 'Codetype    24', \
                    'Codetype   170', 'Codetype   182']
        if ( Variable != 'Z' ): 
            print ("{} variable not supported for SYNOP (only Z)".format(Variable))
            exit()
    elif (Obstype == 'Aircraft'):
        Codetype = ['Codetype   141', 'Codetype   146', 'Codetype   147']
        if ( Variable != 'U' and Variable != 'T'): 
            print ("{} variable not supported for Aircraft (only U and T)".format(Variable))
            exit()

    elif (Obstype == 'Radiosondes'):
        Codetype =  ['Codetype   109 === BUFR Land TEMP' ]
        if ( Variable != 'U' and Variable != 'T' and Variable != 'Q'): 
            print ("{} variable not supported for Radiosondes (only U, T and Q)".format(Variable))
            exit()
    elif (Obstype == 'AMSUA'):
        Codetype = ['Codetype   210 === metop    1     3 SENSOR=amsua', \
                    'Codetype   210 === metop    3     5 SENSOR=amsua', \
                    'Codetype   210 === noaa    18   209 SENSOR=amsua', \
                    'Codetype   210 === noaa    19   223 SENSOR=amsua']
        if ( Variable != 'RAD'): 
            print ("{} variable not supported for AMSUA (only RAD)".format(Variable))
            exit()
    elif (Obstype == 'MHS'): 
        Codetype = ['Codetype   210 === metop    1     3 SENSOR=mhs', \
                    'Codetype   210 === metop    3     5 SENSOR=mhs', \
                    'Codetype   210 === noaa    19   223 SENSOR=mhs']
        if ( Variable != 'RAD'): 
            print ("{} variable not supported for MHS (only RAD)".format(Variable))
            exit()
    elif (Obstype == 'ATMS'): 
        Codetype = ['Codetype   210 === jpss     0   224 SENSOR=atms', \
                     'Codetype   210 === noaa    20   225 SENSOR=atms']
        if ( Variable != 'RAD'): 
            print ("{} variable not supported for ATMS (only RAD)".format(Variable))
            exit()
    elif (Obstype == 'MWHS2'):
        Codetype = ['Codetype   210 === fy3      4', \
                    'Codetype   210 === fy3      5']
        if ( Variable != 'RAD'):
            print ("{} variable not supported for MWHS2 (only RAD)".format(Variable))
            exit()
    elif (Obstype == 'IASI' ):
        Codetype = ['Codetype   210 === metop    1     3 SENSOR=iasi',\
                    'Codetype   210 === metop    3     5 SENSOR=iasi']
        if ( Variable != 'RAD'):
            print ("{} variable not supported for IASI  (only RAD)".format(Variable))
            exit()
    elif (Obstype == 'ASCAT'):
        Codetype = ['Codetype   139 ===  METOP-B ASCAT', 'Codetype   139 ===  METOP-C ASCAT']
        if ( Variable != 'U10'):
            print ("{} variable not supported for ASCAT  (only U10)".format(Variable))
            exit()
    elif (Obstype == 'LIMB'):
        Codetype = ['Codetype   250 === METOP-1', 'Codetype   250 === METOP-3',\
                    'Codetype   250 === SPIRE']
        if ( Variable != 'RO'):
             print ("{} variable not supported for LIMB (only RO)".format(Variable))
             exit()
    elif (Obstype == 'AMV'):
        Codetype = ['Codetype    90 === METOP        5 METHOD=IR',\
                    'Codetype    90 === METEOSAT    56 METHOD=WVCL1',\
                    'Codetype    90 === METEOSAT    56 METHOD=WVCL2', \
                    'Codetype    90 === METEOSAT    56 METHOD=IR3',\
                    'Codetype    90 === METEOSAT    57 METHOD=WVCL1',\
                    'Codetype    90 === METEOSAT    57 METHOD=WVCL2',\
                    'Codetype    90 === METEOSAT    57 METHOD=IR3',\
                    'Codetype    90 === dual-MTOP  852 METHOD=IR']
        if ( Variable != 'U' and Variable != 'T'):
            print ("{} variable not supported for AMV (only U and T)".format(Variable))
            exit()
    else:
        print ("{} Obstype not supported.".format(Obstype))
 
  
    return Codetype
####
def extractJOtable(fileLog, fileJOtable):

    in_JOtable = False
    Readline = False
    myline = []
    fh  = open(fileJOtable, 'w')
    with open (fileLog, 'rt') as myfile:
         for myline in myfile:
           if ("/Mbr000/Analysis/AnUA/Minim.1" in myline):
           #if ("/Mbr016/Analysis/AnUA/Minim.1" in myline):
             Readline = True
             # looks for the start of the minimisation
                # add its contents to mylines.
             #print(myline)
           elif ("/Mbr00" in myline):
           #elif ("/Mbr016" in myline):
             Readline = False
            # print(myline)
           if Readline:
             if("Diagnostic JO-table (JOT) MINIMISATION JOB T0539 NCONF=   131 NSIM4D=     0 NUPTRA=     0" in myline):
                in_JOtable = True
               # print(myline)
             elif("End of JO-table (JOT)" in myline) :
                in_JOtable = False
             # looks for the end of the minimisation
                # add its contents to mylines.
             elif ("Diagnostic JO-table (JOT)" and "MINIMISATION JOB" and "NSIM4D=   999 "  in myline):
                in_JOtable = True
             elif("End of JO-table (JOT)" in myline) :
                in_JOtable = False
             if in_JOtable:
                # print(myline)
                 fh.write(myline)
                 
    fh.close()
####
def readObservations (fileJOtable, code, var):

    in_JOtable = True
    mylines = []
    rec1 = []
    rec2 = []
    nextLine = False
    #
    var = var + " "

    with open (fileJOtable, 'rt') as myfile:
    # searches for codetypes
       for mylines in myfile:
           if (in_JOtable):
              if ( re.search(code, mylines) ):
                 nextLine = True
              if (nextLine):
                 if ( re.search (var , mylines)):
                    record = mylines.split()
                    rec1.append(int(record[1]))
                    #Choisir 3 pour Jo/n (original) et ici 2 pour juste Jo
                    rec2.append(float(record[2]))
                    nextLine = False

              if ("Jo Global :" in mylines ):
                 in_JOtable = False

              in_JOtable = True

    datalist = ({
                  'JoOBS'      : [rec2],
                  'NOBS'       : [rec1]

               })

    return datalist


####
def readGlobal(fileJOtable):

    mylines = []
    rec1 = []
    rec2 = []

    with open(fileJOtable,'rt') as myfile:
     for mylines in myfile:
        if re.search("Jo Global", mylines):
            record = mylines.split()
            rec1.append(int(record[3]))
            rec2.append(float(record[5]))

    datalist = ({
                  'JoGlobal'    : [rec2],
                  'Ntotal'      : [rec1]

               })
    return datalist
#######
def createDataList(data1, data2):

    # sanity test
    if (np.size(data2) == 0) :
        data2[0] = 0
        data1[0] = 0
        data1[1] = 0

    datalist = ({
              'startMinim': [data1[0]],
              'endMinim': [data1[1]],
              'N': [data2[0]],
               })

    return datalist 
#####
def writeJoGlobal(out_path,JoGlobal,name):
       
    filename = '{}/Jo{}.csv'.format(out_path,name)
    df = pd.DataFrame(JoGlobal)
    df.to_csv(filename, index=False, sep =' ')
    #print (">>>>> df: ", df)
    return df

def plotJo(label,path, Jo, Jo1, Jo2, obs, num, cty, var, labelplot):
    
    Jo = Jo.set_index("datetime")
    Jo2 = Jo2.set_index("datetime")
    print ("========= plotting the JO ========")
    png = "{}/Jo{}{}{}_{}.png".format(path,obs,num,var,labelplot)
    plt.close("all")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), gridspec_kw={'height_ratios':[3, 1]})
    ax3 = ax1.twinx()
    ax1.plot(Jo["startMinim"] / Jo["N"],label='start Minim no Mode-S',linestyle='solid',color='darkcyan')
    ax3.plot(Jo["endMinim"] / Jo["N"],label='end Minim no Mode-S',linestyle='solid',color='indianred')
    
    ax1.plot(Jo1["startMinim"] / Jo1["N"],label='start Minim Mode-S',linestyle='solid',color='blue')
    ax3.plot(Jo1["endMinim"] / Jo1["N"],label='end Minim Mode-S',linestyle='solid',color='red')
    ax1.plot(Jo2["startMinim"] / Jo2["N"],label='start substract',linestyle='dotted',color='purple')
    ax3.plot(Jo2["endMinim"] / Jo2["N"],label='end substract',linestyle='dotted',color='brown')
    plt.grid (True)
    ax1.set_ylim(0, 1.0)
    ax3.set_ylim(0, 1.0)
    ax1.set_ylabel("Jo/n")
    
    ax2.plot(Jo["N"].astype(int),label='N',linestyle='dashed',color='grey')
    ax2.set_ylabel ("N")
    legend = ax1.legend(loc='upper left', fontsize='x-small')
    ax3.legend(loc='upper right', fontsize='x-small')
    

    plt.gcf().autofmt_xdate()
    plt.xlabel("Datetime")
    plt.title("{} Cost Function {} {} - {} only".format(labelplot, obs, cty, Variables[0]))
    plt.savefig(png) 
    plt.show() 

    print ("figure saved in: ", png)



if __name__=="__main__": 
    main() 