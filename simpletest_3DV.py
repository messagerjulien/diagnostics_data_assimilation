import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DayLocator, HourLocator
from matplotlib.ticker import (MultipleLocator,
                               FormatStrFormatter,
                               AutoMinorLocator)
import matplotlib.colors as colors
import matplotlib as mpl
import numpy as np
import os
import pandas as pd
import re


#########################################
years = ['2024']
months = ['06']
days = ['01','02','03','04','05','06', '07', '08', '09', '10', '11', '12', '13','14','15','16','17','18','19']#,'20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
cycles = ['12']

paths = ['/scratch/nld5621/logFilesnoModeS', '/scratch/nld5621/logFilesModeS']
out_path = '/scratch/nld5621/logFilesModeS/JBstatistics'
figs = True

#List of the obstypes we want to study
obstypes = ['ObsType  1', 'ObsType  2', 'ObsType  5']
#################################
def main ():
    
    print (">>>> Diagnostics using cost function information from log files <<<<<")
    print (">>>>             Based on J. Barkmeijer code                    <<<<<")
    print (">>>>               Ref. Y. Michel (2014)                           <<<<<")
    results = []
    for path in paths :

        JAll = []
        JOAll = []
        JBAll = []
        date_dfAll = []
        
        for year in years:
            for month in months :

                for day in days:
                    for cy in cycles:
                        try :
                            #Checking if the Jo table is already extracted or not
                            fileLog = '{}/HM_Date_{}{}{}{}.html'.format(path,year,month,day,cy)
                            fileJOtable = '{}/JBstatistics/JOtable_{}{}{}{}.txt'.format(path,year,month,day,cy)
                            if not os.path.isfile(fileLog):
                                        raise FileNotFoundError
                            print(">>>>>>> Reading the log file in: ", fileLog)
                            if not os.path.isfile(fileJOtable):
                                extractJOtable(fileLog, fileJOtable)

                            print(">>>>>>> Reading the log file in: ", fileLog)
                            
                            print(">>>>>>> Reading the JO and JB")

                            CostFunction = readObservations(fileJOtable)
                            df1 = pd.DataFrame(CostFunction['JoOBS'])
                            df2 = pd.DataFrame(CostFunction['NOBS'])
                            df3 = pd.DataFrame(CostFunction['JbOBS'])

                            dataList = createDataList(df1, df2, df3)
                            J = pd.DataFrame(dataList)

                            d = datetime.datetime(int(year),int(month),
                                                    int(day),int(cy)).strftime("%Y-%m-%d %H")
                            date_df = pd.DataFrame ({"datetime": [d]} )
                            JAll.append(J)
                            date_dfAll.append(date_df)
                        except (IOError, FileNotFoundError) as error :
                            pass


        print(">>>>>>> Creating time series of  All Js")
        JAll = pd.concat(JAll, ignore_index=True, axis=0)
        dateAll = pd.concat(date_dfAll, ignore_index= True, axis=0) 
        

        JAll = pd.concat([dateAll, JAll], axis=1)

        print(">>>>>>> writing CostFunctions in :", out_path)
        Jdf = writeJoGlobal(out_path, JAll,'CostFunction')

        results.append(Jdf)
    if (figs): plotJstats (out_path, results[0], results[1])

#######
## In 3D/4D-Var an objective function J is minimized. The cost function consists of three terms:
#  J =Jb +Jo +Jq +Jc (1.1)
#  measuring, respectively, the discrepancy with the background (a short-range forecast started from the previous analysis), 
#  Jb, with the observations, Jo, with the model error, Jq, and with the slow manifold of the atmosphere, Jc. The Jq term is 
#  under active development and is not described further here, but see Fisher et al. (2011). The Jc-term controls the amplitude 
#   of fast waves in the analysis and is described in Chapter 2. It is omitted from the subsequent derivations in this section.

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
                Readline = False
            if Readline:
                if("Diagnostic JO-table (JOT) MINIMISATION JOB T0539 NCONF=   131 NSIM4D=     0 NUPTRA=     0" in myline):
                    in_JOtable = True
                elif("End of JO-table (JOT)" in myline) :
                    in_JOtable = False
                # looks for the end of the minimisation
                    # add its contents to mylines.
                elif ("Diagnostic JO-table (JOT)" and "MINIMISATION JOB" and "NSIM4D=   999 "  in myline):
                    in_JOtable = True
                elif("End of JO-table (JOT)" in myline) :
                    in_JOtable = False
                if in_JOtable:
                    fh.write(myline)
                if ("GREPCOST - ITER,SIM,JO,JB,JC,JQ,JP" in myline):
                    record = myline.split()
                    if (int(record[3]) == 999) :
                        fh.write(myline)
                 
    fh.close()

#######
def readObservations (fileJOtable):
    conv1 = []
    conv2 = []
    conv3 = []
    rec1 = 0
    rec2 = 0.
    rec3 = 0.
    for obstype in obstypes :
        in_JOtable = True
        mylines = []
        

        with open (fileJOtable, 'rt') as myfile:
        # searches for codetypes
            for mylines in myfile:
                if (in_JOtable):
                    if ( re.search(obstype, mylines) ):
                        record = mylines.split()
                        rec1 += int(record[3])
                        rec2 += float(record[4])
                        in_JOtable = False
                if re.search("GREPCOST - ITER,SIM,JO,JB,JC,JQ,JP,JA", mylines):
                    record = mylines.split()
                    if (int(record[3]) == 999) :
                        rec3 += float(record[6])

    conv1.append(rec1)
    conv2.append(rec2)
    conv3.append(rec3)

    datalist = ({
                  'JbOBS'      : [conv3],
                  'JoOBS'      : [conv2],
                  'NOBS'       : [conv1]

               })

    return datalist

#######
def createDataList(data1, data2, data3):

    # sanity test
    if (np.size(data2) == 0) :
        data1[0] = 0
        data2[0] = 0
        data3[0] = 0

        #data3[0] = 0
        #data1[1] = 0  
        #data1[2] = 0 
        #data1[3] = 0 
        #data1[4] = 0 

    datalist = ({
              'JB': [data3[0]],
              'JO': [data1[0]],
              'Ntotal' :     [data2[0]]
                 })

    return datalist
#####
def writeJoGlobal(out_path,JoGlobal,name):
       
    filename = '{}/{}.csv'.format(out_path,name)
    df = pd.DataFrame(JoGlobal)
    df.to_csv(filename, index=False, sep =' ')
    return df

#####
def plotJstats(path, J, J2):

    df = pd.to_datetime(J['datetime'])
    hh = df.dt.hour

    png1 = "{}/ScatterPlotCostFun.png".format(path)
    png2 = "{}/ScatterPlotCostFunNobs.png".format(path)
    plt.close("all")

    rgb_metoffice= [(0,0,100/256.), (80/256.,60/256.,181/256.), (80/256.,140/256.,219/256.),
                    (160/256.,200/256.,255/256.), (119/256.,225/256.,160/256.),
                    (205/256.,255/256.,195/256.), (255/256.,255/256.,190/256.),
                    (231/256.,231/256.,131/256.)]
    palette = colors.ListedColormap(rgb_metoffice, name='my_colormap_name')
    bounds = np.arange(0,27,3)
    norm = mpl.colors.BoundaryNorm(bounds, palette.N)

    palette2 = plt.matplotlib.colors.LinearSegmentedColormap('jet3',plt.cm.datad['jet'],2048)
    
    print ("========= simple test ========")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize= (6, 9))
    ax3 = ax1.twinx()
    ax1.plot(J['JO'] + J['JB'], color = 'gold', label = 'J = Jo + Jb no Mode-S')
    ax3.plot(J['Ntotal'], linestyle = 'dashed', color='grey', label = 'Nb obs no Mode-S')
    
    ax2.plot(((2 * (J['JO']+0.5*J['JB']))/J['Ntotal']), color = 'limegreen', label = '2J/N no Mode-S')
    ax2.axhline(((2 * (J['JO'].mean()+0.5*J['JB'].mean()))/J['Ntotal'].mean()), linestyle = 'dotted')


    ax1.plot(J2['JO']+J2['JB'], color = 'darkorange', label = 'J = Jo + Jb Mode-S')
    ax3.plot(J2['Ntotal'], linestyle = 'dashed', color='grey', label = 'Nb obs Mode-S')
    ax2.plot(((2 * (J2['JO']+0.5*J2['JB']))/J2['Ntotal']), color = 'darkgreen', label = '2J/N Mode-S')
    ax2.axhline(((2 * (J2['JO'].mean()+0.5*J2['JB'].mean()))/J2['Ntotal'].mean()), color = 'purple', linestyle = 'dotted')
    ax2.set_ylim(0.5, 1.6)
    ax1.set_xticks(range(1, 21))
    ax2.set_xticks(np.arange(1, 21, 1))
    ax1.legend(loc='upper left')
    ax3.legend(loc='upper right')
    ax2.legend(loc='upper right')
    plt.title("Value of the cost-function at the minimum at {}".format(cycles[0]))
    plt.savefig(png1) 
    plt.show() 
    print ("figure saved in: ", png1)

    plt.close("all")

    """

    
    
    print ("========= scatterplots ========")
    
    fig = plt.figure

    plt.scatter(x = J['JB'], y = J['JO'], c = J['Ntotal'] , s= 5,  marker = 'x', cmap = palette2)
    plt.xlabel("JO")
    plt.ylabel("JB")
    plt.colorbar(label="Nobs")
    plt.title("Background vs. Observations Cost Function (end Minim)")
    plt.savefig(png2) 
    plt.show() 
    print ("figure saved in: ", png2)
    """
    


if __name__=="__main__": 
    main() 
