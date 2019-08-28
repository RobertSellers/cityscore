import arcpy, sys, string, os
import numpy as np
from scipy.stats import norm

try:

    # def arcgis_table_to_dataframe(in_fc, input_fields, query="", skip_nulls=False, null_values=None):
    #     """Function will convert an arcgis table into a pandas dataframe with an object ID index, and the selected
    #     input fields. Uses TableToNumPyArray to get initial data."""
    #     OIDFieldName = arcpy.Describe(in_fc).OIDFieldName
    #     if input_fields:
    #         final_fields = [OIDFieldName] + input_fields
    #     else:
    #         final_fields = [field.name for field in arcpy.ListFields(in_table)]
    #     np_array = arcpy.da.TableToNumPyArray(in_fc, final_fields, query, skip_nulls, null_values)
    #     object_id_index = np_array[OIDFieldName]
    #     fc_dataframe = pd.DataFrame(np_array, index=object_id_index, columns=input_fields)
    #     return fc_dataframe


    arcpy.env.workspace = "in_memory"
    city_features = arcpy.GetParameterAsText(0)#the raw data table
    score_tree = arcpy.GetParameterAsText(1) #metadata table 
    importance_val = arcpy.GetParameterAsText(2) #not currently functional
    metric_val = arcpy.GetParameterAsText(3) #this is the field to be updated
    target_val = arcpy.GetParameterAsText(4) #high or low, basic calculation
    scores_table = arcpy.GetParameterAsText(6) #the master data table to be updated
    function_val = arcpy.GetParameterAsText(7) 

    #if importance_val == "None":
    arr = arcpy.da.FeatureClassToNumPyArray(city_features, [metric_val])
    mu, std = norm.fit(arr[metric_val])
    #np.savetxt('test.txt', array[metric_val], delimiter=',')
        #data = np.random.normal(loc=5.0, scale=2.0, size=1000)
        #mean,std=norm.fit(data)

    max_value = str(np.max(arr[metric_val]))
    min_value = str(np.min(arr[metric_val]))
    fieldList = [metric_val]
    arcpy.JoinField_management(scores_table, "city", city_features, "city", fieldList)
    # currently only functioning on high vs low
    if target_val == 'High':
        calc = "int(((!" + metric_val + "_1! -" + min_value+ ")/(" + max_value + "-" + min_value + ")) * 100)"
    else: # is Low 0+ %
        calc = "100 - int(((!" + metric_val + "_1! -" + min_value+ ")/(" + max_value + "-" + min_value + ")) * 100)"
    arcpy.CalculateField_management(scores_table, metric_val, calc, "Python")
    arcpy.DeleteField_management(scores_table,metric_val + "_1")
    # update the importance value in score_tree
    with arcpy.da.UpdateCursor(score_tree,['name','importance','target']) as cursor:
        for row in cursor:
            if row[0] == metric_val:
                row[1] = importance_val
                row[2] = target_val
                cursor.updateRow(row)

    arcpy.SetParameter(5, scores_table)

except Exception, ErrorDesc:
    sErr = "ERROR:\n" + str(ErrorDesc)
    arcpy.AddError(sErr)