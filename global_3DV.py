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
days = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16','17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31',]
cycles = ['12']
path1 = '/scratch/nld5621/logFilesnoModeS'
path2 = '/scratch/nld5621/logFilesModeS'
out_path1 = '/scratch/nld5621/logFilesnoModeS/JOstatistics'
out_path2 = '/scratch/nld5621/logFilesModeS/JOstatistics'
labelplot = 'development'
keep_JOtables = True
figs = True
Variable = 'T'
Obstype = 'Aircraft'
#################################
def main ():
    
    print (">>>> Diagnostics using cost function information from log files <<<<<")

    Codetype = SetCodetype(Obstype, Variable)

# Sanity checks
    if (np.size(Codetype) == 0 or  np.size(Variable) == 0):
       print ("ERROR: check your settings for Codetype and Variable")
       print("Codetype: ", Codetype)
       print("Variable : ", Variable)
       exit()
    
    
    num_code = 0
    JoCTydf = []
    for cty in Codetype:
      num_code = num_code + 1 
      JoGlobalAll = []
      JoCtypeAll = []
      date_dfAll = []
    
      for year in years:
        for month in months :

            for day in days:
                  for cy in cycles:
                      try :
                        #Checks if the Jo table has already been extracted or not
                        fileLog = '{}/HM_Date_{}{}{}{}.html'.format(path1,year,month,day,cy)
                        fileJOtable = '{}/JOtable_{}{}{}{}.txt'.format(out_path1,year,month,day,cy)
                        if not os.path.isfile(fileLog):
                                    raise FileNotFoundError
                        print(">>>>>>> Reading the log file in: ", fileLog)
                        if not os.path.isfile(fileJOtable):
                            extractJOtable(fileLog, fileJOtable)
                        
                        #print(">>>>>>> Reading the JoGlobal")
                        Global = readGlobal(fileJOtable)
                        df1 = pd.DataFrame(Global['JoGlobal'])
                        df2 = pd.DataFrame(Global['Ntotal'])
                        dataListG = createDataList(df1, df2)
                        JoGlobal = pd.DataFrame(dataListG)

                        d = datetime.datetime(int(year),int(month),
                                                int(day),int(cy)).strftime("%Y-%m-%d %H")
                        date_df = pd.DataFrame ({"datetime": [d]} )
                        JoGlobalAll.append(JoGlobal)
                        date_dfAll.append(date_df)

                        print(">>>>>>> Reading the Jo{}: ".format(cty))
                        Observations = readObservations(fileJOtable, cty, Variable)
                        df3 = pd.DataFrame(Observations['JoOBS'])
                        df4 = pd.DataFrame(Observations['NOBS'])
                        dataListC =createDataList(df3, df4)
                        JoCTy = pd.DataFrame(dataListC)
                        JoCtypeAll.append(JoCTy)

                        if keep_JOtables is False:
                            print(">>>>>>> deleting: ", fileJOtable)
                            os.remove (fileJOtable)
                      except (IOError, FileNotFoundError) as error :
                        pass

      print(">>>>>>> Creating the list of Jo(s)")
      JoGlobalAll = pd.concat(JoGlobalAll, ignore_index=True, axis=0)
      JoCtypeAll = pd.concat(JoCtypeAll, ignore_index=True, axis=0)
      dateAll = pd.concat(date_dfAll, ignore_index= True, axis=0) 
    

      JoGlobalAll = pd.concat([dateAll, JoGlobalAll], axis=1)
      JoCtypeAll = pd.concat([dateAll, JoCtypeAll], axis=1)

      print(">>>>>>> writing Jo(s) in :", out_path1)
      Jodf = writeJoGlobal(out_path1, JoGlobalAll,"Global")
      JoCTydf.append(writeJoGlobal(out_path1, JoCtypeAll, "Observations_{}_{}".format(Obstype,num_code, Variable)))
      print(">>>>>>> saving Jo(s) plots in :", out_path1)




    num_code = 0

    for cty in Codetype:
      num_code = num_code + 1 
      JoGlobalAll = []
      JoCtypeAll = []
      date_dfAll = []
    
      for year in years:
        for month in months :

            for day in days:
                  for cy in cycles:
                      try :
                        #Checks if the Jo table has already been extracted or not
                        fileLog = '{}/HM_Date_{}{}{}{}.html'.format(path2,year,month,day,cy)
                        fileJOtable = '{}/JOtable_{}{}{}{}.txt'.format(out_path2,year,month,day,cy)
                        if not os.path.isfile(fileLog):
                                    raise FileNotFoundError
                        print(">>>>>>> Reading the log file in: ", fileLog)
                        if not os.path.isfile(fileJOtable):
                            extractJOtable(fileLog, fileJOtable)
                        
                        #print(">>>>>>> Reading the JoGlobal")
                        Global = readGlobal(fileJOtable)
                        df1 = pd.DataFrame(Global['JoGlobal'])
                        df2 = pd.DataFrame(Global['Ntotal'])
                        dataListG = createDataList(df1, df2)
                        JoGlobal = pd.DataFrame(dataListG)

                        d = datetime.datetime(int(year),int(month),
                                                int(day),int(cy)).strftime("%Y-%m-%d %H")
                        date_df = pd.DataFrame ({"datetime": [d]} )
                        JoGlobalAll.append(JoGlobal)
                        date_dfAll.append(date_df)

                        print(">>>>>>> Reading the Jo{}: ".format(cty))
                        Observations = readObservations(fileJOtable, cty, Variable)
                        df3 = pd.DataFrame(Observations['JoOBS'])
                        df4 = pd.DataFrame(Observations['NOBS'])
                        dataListC =createDataList(df3, df4)
                        JoCTy = pd.DataFrame(dataListC)
                        JoCtypeAll.append(JoCTy)

                        if keep_JOtables is False:
                            print(">>>>>>> deleting: ", fileJOtable)
                            os.remove (fileJOtable)
                      except (IOError, FileNotFoundError) as error :
                        pass

      print(">>>>>>> Creating the list of Jo(s)")
      JoGlobalAll = pd.concat(JoGlobalAll, ignore_index=True, axis=0)
      JoCtypeAll = pd.concat(JoCtypeAll, ignore_index=True, axis=0)
      dateAll = pd.concat(date_dfAll, ignore_index= True, axis=0) 
    

      JoGlobalAll = pd.concat([dateAll, JoGlobalAll], axis=1)
      JoCtypeAll = pd.concat([dateAll, JoCtypeAll], axis=1)

      print(">>>>>>> writing Jo(s) in :", out_path2)
      Jodf1 =writeJoGlobal(out_path2, JoGlobalAll,"Global")
      JoCTydf1 = writeJoGlobal(out_path2, JoCtypeAll, "Observations_{}_{}".format(Obstype,num_code, Variable))
      print(">>>>>>> saving Jo(s) plots in :", out_path2)

      if (figs):  plotJo('JoCtype', out_path1, JoCTydf[num_code-1], JoCTydf1, Obstype, num_code, cty, Variable, labelplot)

    if (figs): plotJo('JoGlobal', out_path1, Jodf, Jodf1, "Global","", "", "",labelplot)

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
                    rec2.append(float(record[3]))
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

def plotJo(label,path, Jo, Jo1, obs, num, cty, var, labelplot):

    Jo = Jo.set_index("datetime")
    print ("========= plotting the JO ========")
    png = "{}/Jo{}{}{}_{}.png".format(path,obs,num,var,labelplot)
    plt.close("all")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(Jo["startMinim"].astype(float),label='start Minim no Mode-S',linestyle='solid',color='darkcyan')
    ax.plot(Jo["endMinim"].astype(float),label='end Minim no Mode-S',linestyle='solid',color='indianred')
    ax.plot(Jo1["startMinim"].astype(float),label='start Minim Mode-S',linestyle='solid',color='blue')
    ax.plot(Jo1["endMinim"].astype(float),label='end Minim Mode-S',linestyle='solid',color='red')
    plt.grid (True)
    ax.set_ylim(0,1.0)
    ax.set_ylabel("Jo/n")
    ax2 = ax.twinx()
    ax2.plot(Jo1["N"].astype(int),label='N',linestyle='dashed',color='grey')
    ax2.set_ylabel ("N")
    legend = ax.legend(loc='upper right', fontsize='x-small')
    plt.gcf().autofmt_xdate()
    plt.xlabel("Datetime")
    plt.title("{} Cost Function {} {} - {}".format(labelplot, obs, cty, var))
    plt.savefig(png) 
    plt.show() 

    print ("figure saved in: ", png)



if __name__=="__main__": 
    main() 