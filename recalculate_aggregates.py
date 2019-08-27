import arcpy, sys, string, os
import pandas as pd
    
def arcgis_table_to_dataframe(in_fc, input_fields, query="", skip_nulls=False, null_values=None):
    """Function will convert an arcgis table into a pandas dataframe with an object ID index, and the selected
    input fields. Uses TableToNumPyArray to get initial data."""
    OIDFieldName = arcpy.Describe(in_fc).OIDFieldName
    if input_fields:
        final_fields = [OIDFieldName] + input_fields
    else:
        final_fields = [field.name for field in arcpy.ListFields(in_table)]
    np_array = arcpy.da.TableToNumPyArray(in_fc, final_fields, query, skip_nulls, null_values)
    object_id_index = np_array[OIDFieldName]
    fc_dataframe = pd.DataFrame(np_array, index=object_id_index, columns=input_fields)
    return fc_dataframe

try:
    arcpy.env.workspace = "in_memory"
    score_tree = arcpy.GetParameterAsText(0) #metadata table 
    scores_table = arcpy.GetParameterAsText(1) #the master data table to be checked
    agg_feature = arcpy.GetParameterAsText(2) #the agg  data table to be updated

    # Retrieve fields with data from city calculated data
    fields_wdata = []
    fields = dict((f.name, []) for f in arcpy.ListFields(scores_table) if not f.required)
    rows = arcpy.SearchCursor(scores_table,"","","","")
    for row in rows:
        for f in fields.keys():
            fields[f].append(row.getValue(f))
    for field, values in fields.iteritems():
        if any(map(lambda s: s is None or not str(s).strip(), values)):
            print 'Field: "{}" has empty values'.format(field)
        else:
            # field has values - to be aggregated
            fields_wdata.append(field)
    fields_wdata.remove('city')
    fields_wdata.remove('state')
    df = pd.DataFrame(columns=["firstname", "lastname"])

    # select from score_tree where field is found & calculate intermediaries
    tree_query = "name IN (" + "' - '".replace('-', ",".join('"{}"'.format(i) for i in fields_wdata)) + ")"
    tree_query = tree_query.replace('"', '').replace("' ", "'").replace(" '", "'").replace(",","','")
    fields_subset = ['name', 'dimension', 'indicator', 'importance']
    score_df = arcgis_table_to_dataframe(score_tree, fields_subset, query = tree_query)

    score_df_counts = score_df.groupby(["dimension", "indicator"]).dimension.agg('count').to_frame('count').reset_index()
    score_df = score_df.set_index('indicator').join(score_df_counts.set_index('indicator'), rsuffix='_b').reset_index()
    score_df["importance"] = score_df["importance"].astype(float)
    score_df["multiplier"] = score_df["importance"]/100#.map(multiplier)
    score_df['prptn_indiv'] = score_df['multiplier']/score_df['multiplier'].sum()
    score_df['prprtn_indicator'] = score_df.groupby(['dimension','indicator'])['prptn_indiv'].transform(lambda x: x.sum())
    score_df['prprtn_dimension'] = score_df['prprtn_indicator'].groupby(score_df['dimension']).transform(lambda x:  x/x.sum())

    # organize
    del score_df['dimension_b']
    score_df = score_df[['name','dimension', 'indicator','importance','prptn_indiv','prprtn_indicator','prprtn_dimension','count','multiplier']]
    score_df = score_df.sort_values(by=['dimension', 'indicator'])

    # loop through city predictor calculations
    fields_found = score_df['name'].unique().tolist()
    fields_found.insert(0, 'city')
    raw_df = arcgis_table_to_dataframe(scores_table, fields_found)
    
    # loop through city predictor calculations / Score Tree
    for index, row in score_df.iterrows():
        # loop / use cursor on existing aggregate feature class
        with arcpy.da.UpdateCursor(agg_feature,['city',str(row['indicator'])]) as cursor:
            for r in cursor:
                # gets multiplier from agg master data.  currently need actual city data
                agg_indicator = score_df.loc[score_df['name'] == str(row['name']), 'indicator'].iloc[0]
                indicator_subset = score_df.loc[score_df['indicator'] == agg_indicator]
                cum_sum = 0
                for index, r2 in indicator_subset.iterrows():
                    cur_score = raw_df.loc[raw_df['city'] == r[0], r2['name']].iloc[0]
                    cur_score_product = cur_score * r2['prptn_indiv']
                    cum_sum += cur_score_product / r2['prprtn_indicator']
                r[1] = cum_sum
                cursor.updateRow(r)

    # export data to desktop for Calculation QA
    #export_original = raw_df.to_csv(r'df_tot.csv', index = None, header=True)
    #export_csv = score_df.to_csv (r'df_agg.csv', index = None, header=True)

except Exception, ErrorDesc:
    sErr = "ERROR:\n" + str(ErrorDesc)
    arcpy.AddError(sErr)