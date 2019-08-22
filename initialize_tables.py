import arcpy, sys, string, os

try:
    arcpy.env.workspace = "in_memory"
    scores_fgdb = arcpy.GetParameterAsText(0)
    arcpy.env.workspace = scores_fgdb
    
    if arcpy.Exists("scores_table"):
        fc_cities = scores_fgdb+"/scores_table"
    else:

        city_score_fields = (
            #("city", "TEXT", None),("state", "TEXT", None),
            ("gmp1yr", "DOUBLE"),("gmp3yr", "DOUBLE"),("lightEmit", "DOUBLE"),("deposit5yr", "DOUBLE"),
            ("majLocInd", "DOUBLE"),("majNatInd", "DOUBLE"),("instOutpt", "DOUBLE"),
            ("retailSales", "DOUBLE"),("totalPop", "DOUBLE"),("tradeArSls", "DOUBLE"),
            ("tradeArPop", "DOUBLE"),("unemplRate", "DOUBLE"),("civWrkforc", "DOUBLE"),
            ("medHhInc", "DOUBLE"),("pCapEdu", "DOUBLE"),("goBndRate", "DOUBLE"),
            ("hmless5yr", "DOUBLE"),("hmless10k", "DOUBLE"),("cannib", "DOUBLE"),
            ("mayorTenr", "DOUBLE"),("mayorVtShr", "DOUBLE"),("riskIdxPrs", "DOUBLE"),
            ("whatworks", "DOUBLE"),("openData", "DOUBLE"),("greenIdx", "DOUBLE"),
            ("pCapHsptl", "DOUBLE"),("pCapParks", "DOUBLE"),("pCapSewer", "DOUBLE"),
            ("pctCapEx", "DOUBLE"),("startup", "DOUBLE"),("hiGrowth", "DOUBLE"),
            ("bigTech", "DOUBLE"),("popDens", "DOUBLE"),("coreRvrsn", "DOUBLE"),
            ("fiber", "DOUBLE"),("rsrchUni", "DOUBLE"),("rsrchHsptl", "DOUBLE"),
            ("convSpace", "DOUBLE"),("proSports", "DOUBLE"),("patentGrw", "DOUBLE"),
            ("avgTemp", "DOUBLE"),("dvstyIdx", "DOUBLE"),("costLive", "DOUBLE"),
            ("prvSchCost", "DOUBLE"),("prchPwr", "DOUBLE"),("uniRdpCap", "DOUBLE"),
            ("uniRd5yr", "DOUBLE"),("kwlgWrkrs", "DOUBLE"),("pCapUtil", "DOUBLE"),
            ("jobGwth3yr", "DOUBLE"),("popGwth8yr", "DOUBLE"),("millnPct", "DOUBLE"),
            ("milln5yr", "DOUBLE"),("bachelors", "DOUBLE"),("steamJobs", "DOUBLE"),
            ("steamCmmt", "DOUBLE"),("steamEarn", "DOUBLE"),("steamComp", "DOUBLE"),
            ("sixFigHH", "DOUBLE"),("incInqlty", "DOUBLE"),("houseAppr", "DOUBLE"),
            ("aggInc", "DOUBLE"),("strtDens", "DOUBLE"),("pctDev", "DOUBLE"),
            ("cityAge", "DOUBLE"),("histCore", "DOUBLE"),("meanSlope", "DOUBLE"),
            ("bdrockDpth", "DOUBLE"),("natHaz", "DOUBLE"),("clmteRsli", "DOUBLE"),
            ("nimbyAve", "DOUBLE"),("cstrCstIdx", "DOUBLE"),("cstrUnion", "DOUBLE"),
            ("supplyPipe", "DOUBLE"),("mfStockPct", "DOUBLE"),("prcElasSup", "DOUBLE"),
            ("prcElasDmd", "DOUBLE"),("taxBurden", "DOUBLE"),("taxRate", "DOUBLE"),
            ("pCapPrpTax", "DOUBLE"),("mtg2Rent", "DOUBLE"),("rent2Inc", "DOUBLE"),
            ("aptCPPI", "DOUBLE"),("cppiTrgh", "DOUBLE"),("cprateTrgh", "DOUBLE"),
            ("revPaf3yr", "DOUBLE"),("absrbPace", "DOUBLE"),("trnscVol", "DOUBLE"),
            ("rentOcc", "DOUBLE"),("reMktAve", "DOUBLE"),("reMktSent", "DOUBLE"),
            ("pCapTollRv", "DOUBLE"),("pCapHwy", "DOUBLE"),("airptPGrw", "DOUBLE"),
            ("airptTrvTm", "DOUBLE"),("mobMode", "DOUBLE"),("railSrv", "DOUBLE"),
            ("pMileTrans", "DOUBLE"),("transStops", "DOUBLE"),("trvTmInnr", "DOUBLE"),
            ("interstates", "DOUBLE"),("congCost", "DOUBLE"),("urbanVMT", "DOUBLE"),
            ("avgCommute", "DOUBLE"),("pubTrnsCom", "DOUBLE")) 
        sr = arcpy.SpatialReference(4326)
        fc_cities = arcpy.CreateFeatureclass_management(scores_fgdb, "scores_table", "POINT", spatial_reference=sr)  
        arcpy.CopyFeatures_management("data_xy",fc_cities)
        for fc_field in city_score_fields:  
            arcpy.AddField_management(fc_cities, *fc_field)
    if arcpy.Exists("scores_aggregate"):
        fc_score_agg = scores_fgdb+"/scores_aggregate"
    else:
        sr = arcpy.SpatialReference(4326)
        #fc_score_agg = arcpy.CreateTable_management(scores_fgdb, "scores_aggregate")
        fc_score_agg = arcpy.CreateFeatureclass_management(scores_fgdb, "scores_aggregate", "POINT", spatial_reference=sr)  
        arcpy.CopyFeatures_management("data_xy",fc_score_agg)
        agg_fields = (("composite", "DOUBLE"),("economy", "DOUBLE"),
        ("govern", "DOUBLE"),("growth", "DOUBLE"),
        ("develop", "DOUBLE"),("market", "DOUBLE"),
        ("transport", "DOUBLE"),("govern", "DOUBLE"),
        ("economy", "DOUBLE"),("industry", "DOUBLE"),
        ("jobs", "DOUBLE"),("output", "DOUBLE"),
        ("pop", "DOUBLE"),("trd_area", "DOUBLE"),
        ("spending", "DOUBLE"),("cap_prdct", "DOUBLE"),
        ("leadershp", "DOUBLE"),("progress", "DOUBLE"),
        ("density", "DOUBLE"),("commerce", "DOUBLE"),
        ("instit", "DOUBLE"),("resources", "DOUBLE"),
        ("talent", "DOUBLE"),("steam", "DOUBLE"),
        ("construc", "DOUBLE"),("enviro", "DOUBLE"),
        ("phys", "DOUBLE"),("supply", "DOUBLE"),
        ("momentum", "DOUBLE"),("afforda", "DOUBLE"),
        ("multifam", "DOUBLE"),("pricing", "DOUBLE"),
        ("air", "DOUBLE"),("rail", "DOUBLE"),("invest", "DOUBLE"),("wealth", "DOUBLE"),
        ("road", "DOUBLE"),("usblty", "DOUBLE"),("historic", "DOUBLE"),("homeless", "DOUBLE"),("intellect", "DOUBLE")
        )
        for fc_field in agg_fields:  
            arcpy.AddField_management(fc_score_agg, *fc_field)
    arcpy.SetParameter(1, fc_cities)
    arcpy.SetParameter(2, fc_score_agg)
except Exception, ErrorDesc:
    sErr = "ERROR:\n" + str(ErrorDesc)
    arcpy.AddError(sErr)