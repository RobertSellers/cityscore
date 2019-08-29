import arcpy, sys, string, os

try:

    arcpy.env.workspace = "in_memory"
    scores_fgdb = arcpy.GetParameterAsText(0)
    arcpy.env.workspace = scores_fgdb
    sr = arcpy.SpatialReference(4326)

    if arcpy.Exists("scores_table"):
        fc_cities = scores_fgdb+"/scores_table"

    else:

        city_score_fields = (
            ('gmp1yr', 'FLOAT'),
            ('gmp3yr', 'FLOAT'),
            ('lightEmit', 'FLOAT'),
            ('deposit5yr', 'FLOAT'),
            ('majLocInd', 'SHORT'),
            ('majNatInd', 'SHORT'),
            ('instOutpt', 'FLOAT'),
            ('retailSales', 'FLOAT'),
            ('totalPop', 'LONG'),
            ('tradeArSls', 'LONG'),
            ('tradeArPop', 'LONG'),
            ('unemplRate', 'FLOAT'),
            ('civWrkforc', 'LONG'),
            ('medHhInc', 'LONG'),
            ('pCapEdu', 'FLOAT'),
            ('goBndRate', 'SHORT'),
            ('hmless5yr', 'FLOAT'),
            ('hmless10k', 'LONG'),
            ('cannib', 'FLOAT'),
            ('mayorTenr', 'FLOAT'),
            ('mayorVtShr', 'FLOAT'),
            ('riskIdxPrs', 'SHORT'),
            ('whatworks', 'SHORT'),
            ('openData', 'FLOAT'),
            ('greenIdx', 'FLOAT'),
            ('pCapHsptl', 'FLOAT'),
            ('pCapParks', 'FLOAT'),
            ('pCapSewer', 'FLOAT'),
            ('pctCapEx', 'FLOAT'),
            ('startup', 'FLOAT'),
            ('hiGrowth', 'FLOAT'),
            ('bigTech', 'SHORT'),
            ('popDens', 'FLOAT'),
            ('coreRvrsn', 'FLOAT'),
            ('fiber', 'FLOAT'),
            ('rsrchUni', 'FLOAT'),
            ('rsrchHsptl', 'LONG'),
            ('convSpace', 'LONG'),
            ('proSports', 'SHORT'),
            ('patentGrw', 'FLOAT'),
            ('avgTemp', 'FLOAT'),
            ('dvstyIdx', 'FLOAT'),
            ('costLive', 'FLOAT'),
            ('prvSchCost', 'LONG'),
            ('prchPwr', 'FLOAT'),
            ('uniRdpCap', 'FLOAT'),
            ('uniRd5yr', 'FLOAT'),
            ('kwlgWrkrs', 'FLOAT'),
            ('pCapUtil', 'FLOAT'),
            ('jobGwth3yr', 'FLOAT'),
            ('popGwth8yr', 'FLOAT'),
            ('millnPct', 'FLOAT'),
            ('milln5yr', 'FLOAT'),
            ('bachelors', 'FLOAT'),
            ('steamJobs', 'FLOAT'),
            ('steamCmmt', 'LONG'),
            ('steamEarn', 'FLOAT'),
            ('steamComp', 'LONG'),
            ('sixFigHH', 'FLOAT'),
            ('incInqlty', 'FLOAT'),
            ('houseAppr', 'FLOAT'),
            ('aggInc', 'LONG'),
            ('strtDens', 'FLOAT'),
            ('pctDev', 'FLOAT'),
            ('cityAge', 'LONG'),
            ('histCore', 'FLOAT'),
            ('meanSlope', 'FLOAT'),
            ('bdrockDpth', 'FLOAT'),
            ('natHaz', 'SHORT'),
            ('clmteRsli', 'FLOAT'),
            ('nimbyAve', 'LONG'),
            ('cstrCstIdx', 'FLOAT'),
            ('cstrUnion', 'FLOAT'),
            ('supplyPipe', 'FLOAT'),
            ('mfStockPct', 'FLOAT'),
            ('prcElasSup', 'FLOAT'),
            ('prcElasDmd', 'FLOAT'),
            ('taxBurden', 'FLOAT'),
            ('taxRate', 'FLOAT'),
            ('pCapPrpTax', 'FLOAT'),
            ('mtg2Rent', 'FLOAT'),
            ('rent2Inc', 'FLOAT'),
            ('aptCPPI', 'FLOAT'),
            ('cppiTrgh', 'FLOAT'),
            ('cprateTrgh', 'FLOAT'),
            ('revPaf3yr', 'FLOAT'),
            ('absrbPace', 'LONG'),
            ('trnscVol', 'FLOAT'),
            ('rentOcc', 'FLOAT'),
            ('reMktAve', 'FLOAT'),
            ('reMktSent', 'FLOAT'),
            ('pCapTollRv', 'FLOAT'),
            ('pCapHwy', 'FLOAT'),
            ('airptQual', 'SHORT'),
            ('airptPGrw', 'FLOAT'),
            ('airptTrvTm', 'FLOAT'),
            ('mobMode', 'SHORT'),
            ('railSrv', 'FLOAT'),
            ('pMileTrans', 'LONG'),
            ('transStops', 'SHORT'),
            ('trvTmInnr', 'SHORT'),
            ('interstates', 'SHORT'),
            ('congCost', 'LONG'),
            ('urbanVMT', 'FLOAT'),
            ('avgCommute', 'FLOAT'),
            ('pubTrnsCom', 'FLOAT'),
            )

        fc_cities = arcpy.CreateFeatureclass_management(scores_fgdb, "scores_table", "POINT", spatial_reference=sr)  
        arcpy.CopyFeatures_management("data_xy",fc_cities)
        for fc_field in city_score_fields:  
            arcpy.AddField_management(fc_cities, *fc_field)

    if arcpy.Exists("scores_aggregate"):
        fc_score_agg = scores_fgdb+"/scores_aggregate"

    else:

        #fc_score_agg = arcpy.CreateTable_management(scores_fgdb, "scores_aggregate")
        fc_score_agg = arcpy.CreateFeatureclass_management(scores_fgdb, "scores_aggregate", "POINT", spatial_reference=sr)  
        arcpy.CopyFeatures_management("data_xy",fc_score_agg)
        agg_fields = (
        ("composite", "FLOAT"),("economy", "FLOAT"),
        ("govern", "FLOAT"),("growth", "FLOAT"),
        ("develop", "FLOAT"),("market", "FLOAT"),
        ("transport", "FLOAT"),("govern", "FLOAT"),
        ("economy", "FLOAT"),("industry", "FLOAT"),
        ("jobs", "FLOAT"),("output", "FLOAT"),
        ("pop", "FLOAT"),("trd_area", "FLOAT"),
        ("spending", "FLOAT"),("cap_prdct", "FLOAT"),
        ("leadershp", "FLOAT"),("progress", "FLOAT"),
        ("density", "FLOAT"),("commerce", "FLOAT"),
        ("instit", "FLOAT"),("resources", "FLOAT"),
        ("talent", "FLOAT"),("steam", "FLOAT"),
        ("construc", "FLOAT"),("enviro", "FLOAT"),
        ("phys", "FLOAT"),("supply", "FLOAT"),
        ("momentum", "FLOAT"),("afforda", "FLOAT"),
        ("multifam", "FLOAT"),("pricing", "FLOAT"),
        ("air", "FLOAT"),("rail", "FLOAT"),
        ("invest", "FLOAT"),("wealth", "FLOAT"),
        ("road", "FLOAT"),("usblty", "FLOAT"),("historic", "FLOAT"),
        ("homeless", "FLOAT"),("intellect", "FLOAT")
        )
        for fc_field in agg_fields:  
            arcpy.AddField_management(fc_score_agg, *fc_field)

    arcpy.SetParameter(1, fc_cities)
    arcpy.SetParameter(2, fc_score_agg)
	
except Exception, ErrorDesc:
    sErr = "ERROR:\n" + str(ErrorDesc)
    arcpy.AddError(sErr)