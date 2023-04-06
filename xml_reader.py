# -*- coding: utf-8 -*-
"""
Created on Fri May  1 10:15:10 2020

@author: Edgar Nandayapa
"""

import pandas as pd 
import xml.etree.ElementTree as et
import glob
import os


class xml_reader:

    def find_latest_recipeFile():
        pathRoot = "C:\\LP50\\"
        recipePath = pathRoot+"Recipes\\1 My Recipes\\"

        try:
            list_of_files = glob.glob(recipePath+'*.xml')
            latest_recipeFile = max(list_of_files, key=os.path.getmtime)
        except:
            latest_recipeFile = 0


        print()
        return pathRoot, latest_recipeFile


    def gather_data():
        # filePath = "D:\\Backup\\LP50\\Configuration\\config\\ParameterConfig.par.xml"
        #filePath = pathRoot+"LP50\\HeadAssy\\02 Spectra\\Spectra SE-128_08315J01032_Super Yellow.HeadAssy.xml"
        pathRoot, l_rF = xml_reader.find_latest_recipeFile()
        if l_rF == 0:
            var_dict = {}

            var_dict["NotUsingLP50Computer"] = "True"

            return var_dict

        else:

            filePath = []
            filePath.append(str(pathRoot)+"Settings\\ParameterValues.val.xml")
            filePath.append(str(l_rF))
            # print(l_rF)
            # xml_reader.gather_data(filePath)
    
            # df_cols = ["Name", "Type", "Default", "Value", "Min", "Max", "Unit", "Writable", "Visible", "Description"]
            df_cols = ["Name", "Value"]
            rows = []
            var_dict = {}

            
            for fP in filePath:
                xtree = et.parse(fP)
                xroot = xtree.getroot()
            
                for node in xroot.iter("Parameter"):
                    rows.append(node.attrib)
            
            out_df = pd.DataFrame(rows, columns = df_cols)
            
            ##Recipe.xml data
            var_dict["ActiveNozzles"] = out_df.loc[out_df["Name"] == "DataGen.ActiveNozzles[0]"]["Value"].values[0]#Active Nozzles
            var_dict["PrintSpeed"] = out_df.loc[out_df["Name"] == "Motion.PrintSpeed[0]"]["Value"].values[0] #Print speed
            var_dict["QualityFactor"] = out_df.loc[out_df["Name"] == "Recipe.Mask[0]"]["Value"].values[0] #Quality Factor
            var_dict["PrintAngle"] = out_df.loc[out_df["Name"] == "Recipe.PrintAngle[0]"]["Value"].values[0] #90 = y-normal
            var_dict["XResolution"] = out_df.loc[out_df["Name"] == "Recipe.X_Resolution[0]"]["Value"].values[0] #X-resolution
            var_dict["YResolution"] = out_df.loc[out_df["Name"] == "Recipe.Y_Resolution[0]"]["Value"].values[0] #Y-resolution
            if  out_df.loc[out_df["Name"] == "Recipe.Direction[0]"]["Value"].values[0] == 1: #1:unidirectional, 2:reverse, 3:bidirectional
                var_dict["Directional"] = "Unidirectional"
            elif  out_df.loc[out_df["Name"] == "Recipe.Direction[0]"]["Value"].values[0] == 1:
                var_dict["Directional"] = "Unidirectional_reverse"
            else:
                var_dict["Directional"] = "Bidirectional"
            
            
            #ParameterValues.val.xml data
            var_dict["Recipe_used"] = l_rF.split("\\")[-1]
            var_dict["Printhead_used"] = out_df.loc[out_df["Name"] == "General.ActiveHeadassembly[0]"]["Value"].values[0] #Assembly (printhead) used
            var_dict["SubstrateTemperature"] = out_df.loc[out_df["Name"] == "IO.Substrate.Heater1.TemperatureSetpoint[0]"]["Value"].values[0] #Substrate temperature
            try:
                var_dict["PrintHeadTemperature"] = out_df.loc[out_df["Name"] == "Printhead.Hotmelt.TempActual[0]"]["Value"].values[0] #printhead temperature
            except:
                var_dict["PrintHeadTemperature"] = "NaN"
            var_dict["PressureSetpoint"] = out_df.loc[out_df["Name"] == "IO.Ink.PressureSetpoint[0]"]["Value"].values[0] #Pressure Setpoint
            var_dict["Swaths"] = out_df.loc[out_df["Name"] == "Simulator.NumberOfSwaths[0]"]["Value"].values[0] #Number of Swaths
            
            var_dict["AVoltage"] = out_df.loc[out_df["Name"] == "IO.HeadVoltage.SetRowA[0]"]["Value"].values[0] #Voltage Row A
            var_dict["AMaxVoltPer"] = out_df.loc[out_df["Name"] == "Printhead.Spectra.PulseAv2[0]"]["Value"].values[0] #Pulseshape A - Max Voltage%
            var_dict["AMinVoltPer"] = out_df.loc[out_df["Name"] == "Printhead.Spectra.PulseAv1[0]"]["Value"].values[0] #Pulseshape A - Min Voltage%
            var_dict["ARiseEdge"] = out_df.loc[out_df["Name"] == "Printhead.Spectra.PulseAt1[0]"]["Value"].values[0] #Pulseshape A - Rise edge
            var_dict["APeakTime"] = out_df.loc[out_df["Name"] == "Printhead.Spectra.PulseAt2[0]"]["Value"].values[0] #Pulseshape A - Peak time
            var_dict["AFallEdge"] = out_df.loc[out_df["Name"] == "Printhead.Spectra.PulseAt3[0]"]["Value"].values[0] #Pulseshape A - Falling edge
            
            var_dict["BVoltage"] =  out_df.loc[out_df["Name"] == "IO.HeadVoltage.SetRowB[0]"]["Value"].values[0] #Voltage Row B
            var_dict["BMaxVoltPer"] = out_df.loc[out_df["Name"] == "Printhead.Spectra.PulseBv2[0]"]["Value"].values[0] #Pulseshape B - Max Voltage
            var_dict["BMinVoltPer"] = out_df.loc[out_df["Name"] == "Printhead.Spectra.PulseBv1[0]"]["Value"].values[0] #Pulseshape B - Min Voltage
            var_dict["BRiseEdge"] = out_df.loc[out_df["Name"] == "Printhead.Spectra.PulseBt1[0]"]["Value"].values[0] #Pulseshape B - Rise edge
            var_dict["BPeakTime"] = out_df.loc[out_df["Name"] == "Printhead.Spectra.PulseBt2[0]"]["Value"].values[0] #Pulseshape B - Peak time
            var_dict["BFallEdge"] = out_df.loc[out_df["Name"] == "Printhead.Spectra.PulseBt3[0]"]["Value"].values[0] #Pulseshape B - Falling edge
            
            var_dict["SubstratePosition"] = out_df.loc[out_df["Name"] == "Position.AlignedStartPosition[0]"]["Value"].values[0] #Aligned start position (substrate)
            var_dict["SubstrateHeight"] = out_df.loc[out_df["Name"] == "Position.SubstrateThickness[0]"]["Value"].values[0] #Substrate thickness(substrate)
    
    
            # print(var_dict)
            return var_dict



# if __name__=='__main__':
#     x = xml_reader.__init__(self)
