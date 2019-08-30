import arcpy, sys, string, os
import numpy as np
from numpy import inf
# from scipy.stats import norm,rayleigh
# from scipy.optimize import curve_fit
# from numpy import linspace

try:

    city_features = arcpy.GetParameterAsText(0)
    metric_val = arcpy.GetParameterAsText(1) 
    function_val = arcpy.GetParameterAsText(2)
    arcpy.env.workspace = arcpy.GetParameterAsText(4)

    if function_val != 'None':
        arr = arcpy.da.FeatureClassToNumPyArray(city_features, [metric_val])
        # max_value = np.max(arr[metric_val])
        # min_value = np.min(arr[metric_val])
        arr_len = arr[metric_val].size
        # sd = np.std(arr[metric_val])
        # m = np.mean(arr[metric_val])
        # x = linspace(min_value,max_value,arr_len)

    if function_val == 'Logarithm':
        x = np.logspace(1, 2, num=arr_len)
        y = np.array(arr[metric_val])
        log_arr = np.polyfit( np.log(x), y, 1)
        i = 0
        with arcpy.da.UpdateCursor(city_features, metric_val) as cursor:
            for row in cursor:
                precheck = log_arr[0] + log_arr[1]* np.log(row[0])
                if precheck == float('-inf'):
                    precheck = 0
                row[0] = precheck
                cursor.updateRow(row)
                i += 1

    arcpy.SetParameter(3, city_features)

except Exception, ErrorDesc:
    sErr = "ERROR:\n" + str(ErrorDesc)
    arcpy.AddError(sErr)