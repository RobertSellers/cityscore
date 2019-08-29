import arcpy, sys, string, os
import pandas as pd
    
# utility function to go from arcgis feature class attribute table to pandas dataframe
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

    # Access modelbuilder parameters
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

    # select from score_tree where field is found & calculate intermediaries
    tree_query = "name IN (" + "' - '".replace('-', ",".join('"{}"'.format(i) for i in fields_wdata)) + ")"
    tree_query = tree_query.replace('"', '').replace("' ", "'").replace(" '", "'").replace(",","','")
    fields_subset = ['name', 'dimension', 'indicator', 'importance']

    df_agg = arcgis_table_to_dataframe(score_tree, fields_subset, query = tree_query)
    df_agg_counts = df_agg.groupby(["dimension", "indicator"]).dimension.agg('count').to_frame('count').reset_index()
    df_agg = df_agg.set_index('indicator').join(df_agg_counts.set_index('indicator'), rsuffix='_b').reset_index()
    df_agg["multiplier"] = df_agg["importance"].astype(float)/100
    df_agg['prptn_indiv'] = df_agg['multiplier']/df_agg['multiplier'].sum()
    df_agg['prprtn_indicator'] = df_agg.groupby(['dimension','indicator'])['prptn_indiv'].transform(lambda x: x.sum())
    df_agg['prprtn_dimension'] = df_agg['importance'].astype(float).groupby(df_agg['dimension']).transform(lambda x:  x/x.sum())
    df_agg['prprtn_dimension'] = (df_agg.groupby(['dimension', 'indicator'])['prprtn_dimension'].transform('sum'))
    df_agg_2 =df_agg.groupby(['dimension','indicator'])['prptn_indiv'].agg('sum').reset_index()

    # organize
    del df_agg['dimension_b']
    df_agg = df_agg[['name','dimension', 'indicator','importance','prptn_indiv','prprtn_indicator','prprtn_dimension','count','multiplier']]
    df_agg = df_agg.sort_values(by=['dimension', 'indicator'])

    # loop through city predictor calculations
    fields_found = df_agg['name'].unique().tolist()
    fields_found.insert(0, 'city')
    raw_df = arcgis_table_to_dataframe(scores_table, fields_found)
    agg_calc_cols = ['city', 'dimension', 'indicator', 'cum_sum', 'multiplier']
    lvl2List = []
    # loop through city predictor calculations / Score Tree
    for index, row in df_agg.iterrows():
        # loop / use cursor on existing aggregate feature class
        with arcpy.da.UpdateCursor(agg_feature,['city',str(row['indicator']),str(row['dimension']), 'composite']) as cursor:
            # scores = []
            for r in cursor:

                # update each indicator field (level 3)
                agg_indicator = df_agg.loc[df_agg['name'] == str(row['name']), 'indicator'].iloc[0]
                cum_sum = 0.0
                for index, r2 in df_agg.loc[df_agg['indicator'] == agg_indicator].iterrows():
                    raw_data_score = raw_df.loc[raw_df['city'] == r[0], r2['name']].iloc[0]
                    #scores.append(raw_data_score)
                    cum_sum += (raw_data_score * r2['prptn_indiv']) / r2['prprtn_indicator']
                r[1] = cum_sum

                # this section pre-populates pre-calculated aggregates to feature for dimension. current loop 
                # seems incompatible with adding via cursor
                agg_dimension = df_agg.loc[df_agg['name'] == str(row['name']), 'dimension'].iloc[0]

                for index, r2 in df_agg_2.iterrows():
                    if r2['indicator'] == str(row['indicator']) and r2['dimension'] == str(row['dimension']):
                        lvl2List.append([r[0], row['dimension'], row['indicator'], float(cum_sum), r2['prptn_indiv']])

                cursor.updateRow(r)

    agg_calc_cols = pd.DataFrame(lvl2List, columns=agg_calc_cols)
    agg_calc_cols = agg_calc_cols.drop_duplicates(['city', 'dimension', 'indicator'])
    agg_calc_cols= agg_calc_cols.assign(col = agg_calc_cols.cum_sum * agg_calc_cols.multiplier).groupby(['city','dimension'],as_index=False).col.sum()

    # this section adds pre-calculated aggregates to feature for dimension
    for index, row in df_agg.iterrows():
        # loop / use cursor on existing aggregate feature class
        with arcpy.da.UpdateCursor(agg_feature,['city',str(row['dimension']), 'composite']) as cursor:
            for r in cursor:
                r[1] = 999#agg_calc_cols.loc[(agg_calc_cols['city'] == r[0]) & (str(row['dimension']) == agg_calc_cols['dimension']), 'col'].iloc[0]
                r[2] = 999
                cursor.updateRow(r)

    # export data to desktop for Calculation QA
    #export_original = raw_df.to_csv(r'C:/Users/rober/Desktop/df_tot.csv', index = None, header=True)
    #export_csv = df_agg.to_csv (r'C:/Users/rober/Desktop/df_agg.csv', index = None, header=True)
    #export_csv2 = agg_calc_cols.to_csv (r'C:/Users/rober/Desktop/agg_calc_cols.csv', index = None, header=True)
except Exception, ErrorDesc:
    sErr = "ERROR:\n" + str(ErrorDesc)
    arcpy.AddError(sErr)