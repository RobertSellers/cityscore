# Import system modules
import arcpy

try:

    # Set the parameters
    InputFeatureClass = arcpy.GetParameterAsText(0)
    InputField = arcpy.GetParameterAsText(1)
    InputValue = arcpy.GetParameterAsText(2)
    arcpy.SetParameter(3, InputValue)

except Exception, ErrorDesc:
    sErr = "ERROR:\n" + str(ErrorDesc)
    arcpy.AddError(sErr)