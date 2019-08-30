import arcpy, sys, string, os
import numpy as np
from scipy.stats import norm

try:

    arcpy.env.workspace = "in_memory"
    city_features = arcpy.GetParameterAsText(0)#the raw data table
    score_tree = arcpy.GetParameterAsText(1) #metadata table 
    importance_val = arcpy.GetParameterAsText(2) #not currently functional
    metric_val = arcpy.GetParameterAsText(3) #this is the field to be updated
    target_val = arcpy.GetParameterAsText(4) #high or low, basic calculation
    scores_table = arcpy.GetParameterAsText(6) #the master data table to be updated
    function_val = arcpy.GetParameterAsText(7) #function selected

    arr = arcpy.da.FeatureClassToNumPyArray(city_features, [metric_val])
    max_value = str(np.max(arr[metric_val]))
    min_value = str(np.min(arr[metric_val]))
    fieldList = [metric_val]

    arcpy.JoinField_management(scores_table, "city", city_features, "city", fieldList)
    
    # currently only functioning on high vs low
    calc = "int(((!" + metric_val + "_1! -" + min_value+ ")/(" + max_value + "-" + min_value + ")) * 100)"
    if target_val == 'High':
        pass
    else: # is Low 0+ %
        calc = "100 - " + calc
    arcpy.CalculateField_management(scores_table, metric_val, calc, "Python")
  
    arcpy.DeleteField_management(scores_table, metric_val + "_1")

    # update the importance value in score_tree
    with arcpy.da.UpdateCursor(score_tree,['name','importance','target', 'function']) as cursor:
        for row in cursor:
            if row[0] == metric_val:
                row[1] = importance_val
                row[2] = target_val
                row[3] = function_val
                cursor.updateRow(row)

    arcpy.SetParameter(5, scores_table)

except Exception, ErrorDesc:
    sErr = "ERROR:\n" + str(ErrorDesc)
    arcpy.AddError(sErr)