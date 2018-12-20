import csv
from pandas import DataFrame
import pandas as pd
import sqlite3
import glob
import re
import urllib.request, json
import urllib.parse
import matplotlib.pyplot as plt
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime


pd.set_option('display.expand_frame_repr', False)
pd.options.mode.chained_assignment = None

def ExchangeTickerDownload(market=None, delisted=False):
    MARKET_CODE_DICT = {
        'kospi': 'stockMkt',
        'kosdaq': 'kosdaqMkt',
        'konex': 'konexMkt'
    }

    DOWNLOAD_URL = 'kind.krx.co.kr/corpgeneral/corpList.do'
    params = {'method': 'download'}

    if market.lower() in MARKET_CODE_DICT:
        params['marketType'] = MARKET_CODE_DICT[market]

    if not delisted:
        params['searchType'] = 13

    params_string = urllib.parse.urlencode(params)
    request_url = urllib.parse.urlunsplit(['http', DOWNLOAD_URL, '', params_string, ''])

    df = pd.read_html(request_url, header=0)[0]
    df['종목코드'] = df['종목코드'].map('{:06d}'.format)

    return df

def ExchangeEvaluator(Ticker):
    KOSPIList = list(ExchangeTickerDownload(market='kospi')['종목코드'])
    KOSDAQList = list(ExchangeTickerDownload(market='kosdaq')['종목코드'])
    if str(Ticker) in KOSPIList:
        return Ticker + '.KS'
    elif str(Ticker) in KOSDAQList:
        return Ticker + '.KQ'

def DFtoSQL(DF, Directory, DBName, TableName):
    Path = Directory + str(DBName) + '.db'
    print(Path)
    con = sqlite3.connect(Path)
    return DF.to_sql(TableName, con = con, if_exists = 'replace')

def FSSFinancialStatement():
    pd.set_option('display.expand_frame_repr', False)

    import time
    import glob

    start = time.time()

    DirectoryList = (glob.glob("C:\\Users\Sejoon_Lim\Desktop\\FSSText/*.txt")) #Search all text files

    FileWriteCount = 1
    for Directory in DirectoryList:
        DirectoryName = str(Directory.split('\\')[-1].split('.')[0]) #2018_사업보고서_04_현금흐름표_연결_20181130
        print(DirectoryName)
        with open(Directory) as txt:
            Lines = txt.readlines()
            ListofList = []
            for Line in Lines:
                LineSplit = Line.split('\t')
                LineSplit[-1] = LineSplit[-1].replace('\n', '')
                for i in range(0, len(LineSplit)):
                    if LineSplit[i] == '':
                        LineSplit[i] = None
                ListofList.append(LineSplit)

            Headers = ListofList.pop(0)
            print(Headers)
            if Headers[-1] == None:
                del Headers[-1]
            print(Headers)
            df = DataFrame(ListofList, columns=Headers)
            df = df.loc[:, df.columns.notnull()] #Delete entire column with column name value'NaN'

            df['종목코드'] = df['종목코드'].str.replace('[', '')
            df['종목코드'] = df['종목코드'].str.replace(']', '')
            # 개별 재무제표 생성 완료



            CompanyNameList = list(set(df['회사명'].tolist())) #전체 상장기업 회사명 리스트
            CompanyTickerList = list(set(df['종목코드'].tolist()))
            for CompanyTicker in CompanyTickerList:
                DFCompanyReport = df.loc[df['종목코드'] == CompanyTicker]
                DFCompanyReport = DFCompanyReport.reset_index(drop=True)
                YearName = DirectoryName.split('_')[0]
                print(DirectoryName)

                HangulQuarter = DirectoryName.split('_')[1]
                if HangulQuarter == '1분기보고서':
                    QuarterName = '1Q'
                elif HangulQuarter == '반기보고서':
                    QuarterName = '2Q'
                elif HangulQuarter == '3분기보고서':
                    QuarterName = '3Q'
                elif HangulQuarter == '사업보고서':
                    QuarterName = '4Q'

                HangulReportName = DirectoryName.split('_')[3]
                if HangulReportName == '재무상태표':
                    ReportName = 'BS' #Balance Sheet
                elif HangulReportName == '포괄손익계산서':
                    ReportName = 'AIS' #Accumulated Income Statement
                elif HangulReportName == '손익계산서':
                    ReportName = 'IS' #Income Statement
                elif HangulReportName == '현금흐름표':
                    ReportName = 'CF' #Cash Flow
                # elif HangulReportName == '자본변동표':
                #     ReportName = 'CE' #Changes in Equity


                #0-연도 1-분기 2-재무제표번호 3-재무제표 종류 4-연결? (-1)-결산일(연결 아니면 4)

                if DirectoryName.split('_')[4] == '연결':
                    ConsolidateName = '_Con'
                else:
                    ConsolidateName = ''

                print(df.shape[1])

                TableName = CompanyTicker + '_' + YearName + '_' + QuarterName + '_' + ReportName + ConsolidateName
                print(TableName)
                FileName = 'C:\\Users\Sejoon_Lim\Desktop\Pickles\\'+ TableName + '.pkl'
                DFCompanyReport.to_pickle(FileName)
                # DFtoSQL(DF = DFCompanyReport, Directory = 'C:\\Users\Sejoon_Lim\Desktop\FinancialStatements\\', DBName=CompanyTicker, TableName = TableName)
                print('파일 저장 횟수 : ', FileWriteCount)
                print('\n')
                FileWriteCount += 1



    end = time.time()

    print(end - start)

#
# class InvestmentIndex:
#     Ticker = input('입력 : ')
#     DBName = Ticker + '.db'
#     DBDirectory = 'C:\\Users\Sejoon_Lim\Google 드라이브\FSSSQL\\' + DBName
#     con = sqlite3.connect(DBDirectory)
#
#     def PER(self):
#         Year = ['_2015', '_2016', '_2017', '_2018']
#         Quarter = ['_1Q', '_2Q', '_3Q', '_4Q']
#         ReportType = ['_BS', '_IS', '_IS1', '_CF']
#         Consolidate = '_Con'
#         # for R in ReportType:
#         #     for Y in Year:
#         #         if Y == '_2015':
#         #             Q = '_4Q'
#         #             continue
#         #             print(self.Ticker + Y + Q + R)
#         #             print(self.Ticker + Y + Q + R + Consolidate)
#         #         else:
#         #             for Q in Quarter:
#         #                 continue
#         #                 print(self.Ticker + Y + Q + R)
#         #                 print(self.Ticker + Y + Q + R + Consolidate)
#
#         TableNameList = []
#
#         for Y in Year:
#             if Y == '_2015':
#                 Q = '_4Q'
#                 TableName = self.Ticker + '%s%s_IS_Con'%(Y, Q)
#                 TableNameList.append(TableName)
#             else:
#                 for Q in Quarter:
#                     TableName = self.Ticker + '%s%s_IS_Con'%(Y, Q)
#                     TableNameList.append(TableName)
#
#         for TableName in TableNameList:
#             pass

    # def PER(self):
    #     print(self.con)
    #     df = pd.read_sql('SELECT * FROM LG_2018_3Q_BS', con = self.con)
    #     print(df)
# FSSFinancialStatement()
# pd.set_option('display.expand_frame_repr', False)
# df = pd.read_pickle('C:\\Users\Sejoon_Lim\Desktop\Pickles\\001430.pkl')
# print(df['항목코드'])
def AlphaVantage(Ticker):
    Link = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + str(Ticker) + '&outputsize=full&apikey=TZJDZZJVQRB8LRG7'
    with urllib.request.urlopen(Link) as url:
        data = json.loads(url.read().decode())['Time Series (Daily)']
    DateList = [*data]
    OHLCDictList = []
    for Date in DateList:
        OHLCDict = data[Date]
        OHLCDict['0. date'] = Date
        OHLCDictList.append(OHLCDict)
    df = DataFrame(OHLCDictList)
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    df = df.set_index('Date')
    df.index = pd.to_datetime(df.index)
    return df

def ReportDictPair(ReportName, ReportType, DictPair):
    FileName = 'C:\\Users\Sejoon_Lim\Desktop\Pickles\\' + ReportName + '.pkl'
    # print(ReportName)
    df = pd.read_pickle(FileName)
    IndexNum = int(df.loc[df['항목코드'] ==  str(ReportType)].index[0])
    # print(IndexNum)
    ColumnNumber = int(df.columns.get_loc('항목명')) + 1

    ValueName = df.iloc[IndexNum]['항목코드']

    ClosingDate = df.iloc[IndexNum]['결산기준일']# 결산기준일
    ClosingDate = datetime.strptime(ClosingDate, '%Y-%m-%d').date()
    ReportValue = df.iloc[IndexNum][ColumnNumber]
    # print(ReportValue, '\n\n')
    DictPair[ClosingDate] = ReportValue
    return DictPair

def HangulReportDictPair(ReportName, ReportType, DictPair):
    FileName = 'C:\\Users\Sejoon_Lim\Desktop\Pickles\\' + ReportName + '.pkl'
    # print(ReportName)
    df = pd.read_pickle(FileName)
    IndexNum = int(df.loc[df['항목명'] ==  str(ReportType)].index[0])
    # print(IndexNum)
    ColumnNumber = int(df.columns.get_loc('항목명')) + 1

    ValueName = df.iloc[IndexNum]['항목코드']

    ClosingDate = df.iloc[IndexNum]['결산기준일']  # 결산기준일
    ClosingDate = datetime.strptime(ClosingDate, '%Y-%m-%d').date()
    ReportValue = df.iloc[IndexNum][ColumnNumber]
    # print(ReportValue, '\n\n')
    DictPair[ClosingDate] = ReportValue
    return DictPair


def FinancialIndex():
    StockCode = input('입력? : ')
    DirectoryList = (glob.glob("C:\\Users\Sejoon_Lim\Desktop\\Pickles/*.pkl"))  # 전체 피클 데이터 검색
    ReportList = []
    for Directory in DirectoryList: #해당 종목의 전체 보고서 목록 생성
        ReportName = str(Directory.split('\\')[-1].split('.')[0])
        ReportAvailable = ReportName.find(StockCode)
        if ReportAvailable != -1:
            ReportList.append(ReportName) #해당 종목의 전체 보고서 목록

    ConISReport = []
    ISReport = []
    ConAISReport = []
    AISReport = []

    ConBSReport = []
    BSReport = []

    ConCFReport = []
    CFReport = []

    for Report in ReportList:
        if Report.split('_')[-1] == 'Con' and Report.split('_')[-2] == 'IS':
            ConISReport.append(Report)

        if Report.split('_')[-1] == 'IS':
            ISReport.append(Report)

        if Report.split('_')[-1] == 'Con' and Report.split('_')[-2] == 'AIS':
            ConAISReport.append(Report)

        if Report.split('_')[-1] == 'AIS':
            AISReport.append(Report)



        if Report.split('_')[-1] == 'Con' and Report.split('_')[-2] == 'BS':
            ConBSReport.append(Report)

        if Report.split('_')[-1] == 'BS':
            BSReport.append(Report)


        if Report.split('_')[-1] == 'Con' and Report.split('_')[-2] == 'CF':
            ConCFReport.append(Report)

        if Report.split('_')[-1] == 'CF':
            CFReport.append(Report)

    ###############################
    #######  ProfitLoss ###########
    ###############################
    if True == True:
        RawProfitLossDict = {}
        if len(ConISReport) > 0:
            for Report in ConISReport:
                ProfitLossDict = ReportDictPair(ReportName = Report, ReportType= 'ifrs_ProfitLossAttributableToOwnersOfParent', DictPair=RawProfitLossDict)
        elif len(ConAISReport) > 0:
            for Report in ConAISReport:
                ProfitLossDict = ReportDictPair(ReportName = Report, ReportType= 'ifrs_ProfitLossAttributableToOwnersOfParent', DictPair=RawProfitLossDict)
        elif len(AISReport) > 0:
            for Report in AISReport:
                ProfitLossDict = ReportDictPair(ReportName = Report, ReportType= 'ifrs_ProfitLoss', DictPair=RawProfitLossDict)
        else:
            ProfitLossDict = {}

        ProfitLossDF = DataFrame(list(ProfitLossDict.items()), columns= ['Date', 'CumulativeProfitLoss']) #분기별 정리 이전
        ProfitLossDF['CumulativeProfitLoss'] = ProfitLossDF["CumulativeProfitLoss"].str.replace(",","").astype(float)
        ProfitLossDF = ProfitLossDF.set_index('Date')
        ProfitLossDF.index = pd.to_datetime(ProfitLossDF.index)
        ProfitLossDF['ProfitLoss'] = None

        ProfitLossDF_FiscalYearList = []
        for Date in ProfitLossDF.index:
            if Date.month == 12:
                ProfitLossDF_FiscalYearList.append(Date)

        for Year in list(set(ProfitLossDF.index.year)):
            # for Month in OACashFlowDF.index.month:
            YearDF = ProfitLossDF.loc[(ProfitLossDF.index.year == Year)]
            DateList = YearDF.index
            DateValueList = []
            print(DateList)
            for Date in DateList:
                if Date.month != 12:
                    ProfitLossDF['ProfitLoss'][Date] = YearDF['CumulativeProfitLoss'][Date]
                    if len(DateList) == 4:
                        DateValueList.append(YearDF['CumulativeProfitLoss'][Date])
                    else:
                        pass

            for FiscalYear in ProfitLossDF_FiscalYearList:
                if FiscalYear.year == Year:
                    ProfitLossDF['ProfitLoss'][FiscalYear] = ProfitLossDF['CumulativeProfitLoss'][FiscalYear] - sum(DateValueList)
        del ProfitLossDF['CumulativeProfitLoss']
        ProfitLossDF = ProfitLossDF.drop(ProfitLossDF.index[0])

        # print(ProfitLossDF_FiscalYearList)
        # for Year in ProfitLossDF_FiscalYearList:
        #     IndexNumber = ProfitLossDF.loc[ProfitLossDF.index == Year].index[0]
        #     if IndexNumber - 4 >= 0:
        #         Sum_123Q = ProfitLossDF['ProfitLoss'].iloc[IndexNumber-3 : IndexNumber].sum()
        #         FiscalYearValue = float(ProfitLossDF['ProfitLoss'][IndexNumber])
        #         ProfitLossDF['ProfitLoss'][IndexNumber] = FiscalYearValue - Sum_123Q
        #     else:
        #         continue

    ###############################
    ##########  Equity  ###########
    ###############################
    if True == True:
        RawEquityDict = {}
        if len(ConBSReport) > 0:
            for Report in ConBSReport:
                EquityDict = ReportDictPair(ReportName = Report, ReportType= 'ifrs_EquityAttributableToOwnersOfParent', DictPair=RawEquityDict)
        elif len(BSReport) > 0:
            for Report in BSReport:
                EquityDict = ReportDictPair(ReportName = Report, ReportType= 'ifrs_Equity', DictPair=RawEquityDict)

        EquityDF = DataFrame(list(EquityDict.items()), columns= ['Date', 'Equity'])
        EquityDF['Equity'] = EquityDF["Equity"].str.replace(",", "").astype(float)

        EquityDF = EquityDF.set_index('Date')
        EquityDF.index = pd.to_datetime(EquityDF.index)

    ###############################
    ##########  Sales  ###########
    ###############################
    if True == True:
        RawRevenueDict = {}
        if len(ConISReport) > 0:
            for Report in ConISReport:
                RevenueDict = ReportDictPair(ReportName=Report, ReportType='ifrs_Revenue', DictPair=RawRevenueDict)
        elif len(ConAISReport) > 0:
            for Report in ConAISReport:
                RevenueDict = ReportDictPair(ReportName=Report, ReportType='ifrs_Revenue', DictPair=RawRevenueDict)
        elif len(AISReport) > 0:
            for Report in AISReport:
                RevenueDict = ReportDictPair(ReportName=Report, ReportType='ifrs_Revenue', DictPair=RawRevenueDict)

        RevenueDF = DataFrame(list(RevenueDict.items()), columns=['Date', 'CumulativeProfitLoss'])  # 분기별 정리 이전
        RevenueDF['CumulativeProfitLoss'] = RevenueDF["CumulativeProfitLoss"].str.replace(",", "").astype(float)
        RevenueDF = RevenueDF.set_index('Date')
        RevenueDF.index = pd.to_datetime(RevenueDF.index)
        RevenueDF['Revenue'] = None

        RevenueDF_FiscalYearList = []
        for Date in RevenueDF.index:
            if Date.month == 12:
                RevenueDF_FiscalYearList.append(Date)


        for Year in list(set(RevenueDF.index.year)):
            # for Month in OACashFlowDF.index.month:
            YearDF = RevenueDF.loc[(RevenueDF.index.year == Year)]
            DateList = YearDF.index
            DateValueList = []
            for Date in DateList:
                if Date.month != 12:
                    RevenueDF['Revenue'][Date] = YearDF['CumulativeProfitLoss'][Date]
                    if len(DateList) == 4:
                        DateValueList.append(YearDF['CumulativeProfitLoss'][Date])
                    else:
                        pass


            for FiscalYear in RevenueDF_FiscalYearList:
                if FiscalYear.year == Year:
                    RevenueDF['Revenue'][FiscalYear] = RevenueDF['CumulativeProfitLoss'][FiscalYear] - sum(
                        DateValueList)
        del (RevenueDF['CumulativeProfitLoss'])
        RevenueDF = RevenueDF.drop(RevenueDF.index[0])

    ###############################
    ########  OA Cash Flow  #######
    ###############################
    if True == True:
        RawOACashFlowDict = {}
        if len(ConCFReport) > 0:
            for Report in ConCFReport:
                OACashFlowDict = ReportDictPair(ReportName=Report, ReportType='ifrs_CashFlowsFromUsedInOperatingActivities', DictPair=RawOACashFlowDict)
        elif len(CFReport) > 0:
            for Report in CFReport:
                OACashFlowDict = ReportDictPair(ReportName=Report, ReportType='ifrs_CashFlowsFromUsedInOperatingActivities', DictPair=RawOACashFlowDict)
        OACashFlowDF = DataFrame(list(OACashFlowDict.items()), columns=['Date', 'CumulativeOACashFlow'])  # 분기별 정리 이전
        OACashFlowDF['CumulativeOACashFlow'] = OACashFlowDF["CumulativeOACashFlow"].str.replace(",", "").astype(float)
        OACashFlowDF = OACashFlowDF.drop(OACashFlowDF.index[0])

        OACashFlowDF['OACashFlow'] = None

        OACashFlowDF = OACashFlowDF.set_index('Date')
        OACashFlowDF.index = pd.to_datetime(OACashFlowDF.index)

        for Year in list(set(OACashFlowDF.index.year)):
            # for Month in OACashFlowDF.index.month:
            YearDF = OACashFlowDF.loc[(OACashFlowDF.index.year == Year)]
            ReversedDateList = list(YearDF.index)[::-1]
            for Date in ReversedDateList:
                CurrentDateIndex = ReversedDateList.index(Date)
                if CurrentDateIndex + 2 <= len(ReversedDateList):
                    PreviousDateIndexValue = ReversedDateList[CurrentDateIndex + 1]
                    OACashFlowDF['OACashFlow'][Date] = OACashFlowDF['CumulativeOACashFlow'][Date] - OACashFlowDF['CumulativeOACashFlow'][PreviousDateIndexValue]


                if Date.month == 3:
                    OACashFlowDF['OACashFlow'][Date] =  OACashFlowDF['CumulativeOACashFlow'][Date]

        del OACashFlowDF['CumulativeOACashFlow']

    ###############################
    #######  OA Depreciation  #####
    ###############################]
    if True == True:
        try:
            RawOADepriciation = {}
            if len(ConCFReport) > 0:
                for Report in ConCFReport:
                    OADepriciationDict = HangulReportDictPair(ReportName=Report,
                                                       ReportType='      조정',
                                                       DictPair=RawOADepriciation)
            elif len(CFReport) > 0:
                for Report in CFReport:
                    OADepriciationDict = HangulReportDictPair(ReportName=Report,
                                                       ReportType='   당기순이익조정을 위한 가감',
                                                       DictPair=RawOADepriciation)

            OADepriciationDF = DataFrame(list(OADepriciationDict.items()), columns=['Date', 'CumulativeOADepriciation'])  # 분기별 정리 이전
            OADepriciationDF['CumulativeOADepriciation'] = OADepriciationDF["CumulativeOADepriciation"].str.replace(",", "").astype(float)
            OADepriciationDF = OADepriciationDF.set_index('Date')
            OADepriciationDF = OADepriciationDF.drop(OADepriciationDF.index[0])


            OADepriciationDF['OADepriciation'] = None
            OADepriciationDF.index = pd.to_datetime(OADepriciationDF.index)

            for Year in list(set(OADepriciationDF.index.year)):
                YearDF = OADepriciationDF.loc[(OADepriciationDF.index.year == Year)]
                ReversedDateList = list(YearDF.index)[::-1]
                for Date in ReversedDateList:
                    CurrentDateIndex = ReversedDateList.index(Date)
                    if CurrentDateIndex + 2 <= len(ReversedDateList):
                        PreviousDateIndexValue = ReversedDateList[CurrentDateIndex + 1]
                        OADepriciationDF['OADepriciation'][Date] = OADepriciationDF['CumulativeOADepriciation'][Date] - OADepriciationDF['CumulativeOADepriciation'][PreviousDateIndexValue]


                    if Date.month == 3:
                        OADepriciationDF['OADepriciation'][Date] =  OADepriciationDF['CumulativeOADepriciation'][Date]

            del OADepriciationDF['CumulativeOADepriciation']
        except:
            OADepriciationDF = DataFrame({'Date' : RevenueDF.index})
            OADepriciationDF['OADepriciation'] = None
            print(OADepriciationDF)
            OADepriciationDF = OADepriciationDF.set_index('Date')

    ##############################
    ##########  Cash  ############
    ##############################
    if True == True:
        RawCashDict = {}
        if len(ConBSReport) > 0:
            for Report in ConBSReport:
                CashDict = ReportDictPair(ReportName = Report, ReportType= 'ifrs_CashAndCashEquivalents', DictPair=RawCashDict)
        elif len(BSReport) > 0:
            for Report in BSReport:
                CashDict = ReportDictPair(ReportName = Report, ReportType= 'ifrs_CashAndCashEquivalents', DictPair=RawCashDict)

        CashDF = DataFrame(list(CashDict.items()), columns= ['Date', 'Cash'])
        CashDF['Cash'] = CashDF["Cash"].str.replace(",", "").astype(float)

        CashDF = CashDF.set_index('Date')
        CashDF.index = pd.to_datetime(CashDF.index)

    ###############################
    ##########  Liabilities  #####
    ##############################
    if True == True:
        RawLiabilitiesDict = {}
        if len(ConBSReport) > 0:
            for Report in ConBSReport:
                LiabilitiesDict = ReportDictPair(ReportName=Report, ReportType='ifrs_Liabilities',
                                          DictPair=RawLiabilitiesDict)
        elif len(BSReport) > 0:
            for Report in BSReport:
                LiabilitiesDict = ReportDictPair(ReportName=Report, ReportType='ifrs_Liabilities',
                                          DictPair=RawLiabilitiesDict)

        LiabilitiesDF = DataFrame(list(LiabilitiesDict.items()), columns=['Date', 'Liabilities'])
        LiabilitiesDF['Liabilities'] = LiabilitiesDF["Liabilities"].str.replace(",", "").astype(float)

        LiabilitiesDF = LiabilitiesDF.set_index('Date')
        LiabilitiesDF.index = pd.to_datetime(LiabilitiesDF.index)

    FinancialStatementDF = EquityDF.join(RevenueDF).join(OACashFlowDF).join(OADepriciationDF).join(LiabilitiesDF).join(CashDF).join(ProfitLossDF)

    ###############################
    #######  Close Price  ########
    ##############################
    if True == True:
        FinancialStatementDateList = FinancialStatementDF.index
        PriceDF = AlphaVantage(ExchangeEvaluator(StockCode))
        StartDate = FinancialStatementDateList[0]

        mask = (PriceDF.index > StartDate)
        PriceDF = PriceDF.loc[mask]
        PriceCloseVolDF = PriceDF[['Close', 'Volume']]
        PriceCloseVolDF = PriceCloseVolDF.sort_index()
        PriceCloseVolDF = PriceCloseVolDF.astype(float)

        PriceCloseVolDF['MarketCap'] = PriceCloseVolDF['Close'] * PriceCloseVolDF['Volume']

    ###############################
    #######  EPS  ################
    ##############################
    # print(PriceCloseVolDF)
    if True == True:
        RawEPSDict = {}
        if len(ConISReport) > 0:
            for Report in ConISReport:
                EPSDict = ReportDictPair(ReportName = Report, ReportType= 'ifrs_BasicEarningsLossPerShare', DictPair=RawEPSDict)
        elif len(ConAISReport) > 0:
            for Report in ConAISReport:
                EPSDict = ReportDictPair(ReportName = Report, ReportType= 'ifrs_BasicEarningsLossPerShare', DictPair=RawEPSDict)
        elif len(AISReport) > 0:
            for Report in AISReport:
                EPSDict = ReportDictPair(ReportName = Report, ReportType= 'ifrs_BasicEarningsLossPerShare', DictPair=RawEPSDict)
        else:
            EPSDict = {}

        EPSDF = DataFrame(list(EPSDict.items()), columns= ['Date', 'EPS']) #분기별 정리 이전
        EPSDF['EPS'] = EPSDF["EPS"].str.replace(",","").astype(float)
        EPSDF = EPSDF.set_index('Date')
        EPSDF.index = pd.to_datetime(EPSDF.index)

    print(EPSDF)
    ###############################
    ##########  PER  #############
    ##############################


    # if True == True:
    #     PERVolume = PriceCloseVolDF['Volume'].sort_index()
    #     PERClosePrice = PriceCloseVolDF['Close'].sort_index()
    #     PERProfitLossDF = FinancialStatementDF['ProfitLoss']
    #     PERProfitLossDF = PERProfitLossDF.reindex(PERVolume.index)
    #
    #     PERDict = {}
    #     PERQuarterDateList = FinancialStatementDF.index
    #     print(PERProfitLossDF)
    #
    #     for Date in PERProfitLossDF.index:
    #         for QuarterDate in PERQuarterDateList:
    #             IndexNum = int(PERQuarterDateList.get_loc(QuarterDate))
    #             if len(PERProfitLossDF.index) > IndexNum + 2:
    #                 if (Date >= QuarterDate) & (Date < PERQuarterDateList[IndexNum + 1]):
    #                     print(Date, ' ', QuarterDate)
    #
    #         # if (len(PERQuarterDateList) > IndexNum + 1):
    #             #     if (Date >= QuarterDate) & (Date < PERQuarterDateList[IndexNum + 1]):
    #             #         try:
    #             #             PERProfitLossDF[Date] = PERProfitLossDF[QuarterDate]
    #             #             print(Date)
    #             #             print(PERProfitLossDF[Date])
    #             #             print(PERVolume[Date])
    #             #             print(PERClosePrice[Date])
    #             #             print('\n\n')
    #     # for QuarterDate in PERQuarterDateList:
    #     #     IndexNum = int(PERQuarterDateList.get_loc(QuarterDate)) #Accessing index number of Datetimeindex
    #     #     print(IndexNum)
    #     #
    #
    #     # print(FinancialStatementDF)
    #     # PERQuarterDateList = FinancialStatementDF.index
    #     #
    #     # for Year in list(set(PERProfitLossDF.index.year)):
    #     #     for Month in list(set(PERProfitLossDF.index.month)):
    #     #         for Day in list(PERProfitLossDF.index.day):
    #     #
    #     # for QuarterDate in PERQuarterDateList:
    #     #     IndexNum = int(PERQuarterDateList.get_loc(QuarterDate)) #Accessing index number of Datetimeindex
    #     #     for Date in PERProfitLossDF.index:
    #     #         print('Date : ', Date)
    #     #         if (len(PERQuarterDateList) > IndexNum + 1):
    #     #             if (Date >= QuarterDate) & (Date < PERQuarterDateList[IndexNum + 1]):
    #     #                 try:
    #     #                     PERProfitLossDF[Date] = PERProfitLossDF[QuarterDate]
    #     #                     print(Date)
    #     #                     print(PERProfitLossDF[Date])
    #     #                     print(PERVolume[Date])
    #     #                     print(PERClosePrice[Date])
    #     #                     print('\n\n')
    #     #                     PERValue = PERVolume[Date] * PERClosePrice[Date] / PERProfitLossDF[Date]
    #     #                     PERDict[Date] = PERValue
    #     #                 except Exception as e:
    #     #                     pass
    #     #         else:
    #     #             pass
    #     # print(PERDict)
    #     # PERDF = DataFrame(list(PERDict.items()), columns=['Date', 'PER'])
    #     # PERDF = PERDF.set_index('Date')
    #     #
    #     # print(PERDF)
    #         # try:
    #         #     PERValue = PERVolume[Date] / PERProfitLoss[Date]
    #         #     PERDict[Date] = PERValue
    #         # except:
    #         #     PERValue = None
    #         #     PERDict[Date] = PERValue
    #     # print(PERDict)
    #     # PERDF = DataFrame(PERDict, columns=['Date', 'PER'])
    #     # PERDF.set_index('Date')
    #
    #     # print(PERDF)
    # # InvestmentIndexDF = PriceCloseVolDF.join(PERDF)
    #
    # # print(InvestmentIndexDF)
    # # # for Date in ClosePriceDF.index:
    # # #     BasisPrice = ClosePriceDF.loc[0]['Close']
    # # #     ComparisonPrice = ClosePriceDF['Close'][Date]
    # # #
    # # #     ComparisonAnalysisPrice = ComparisonPrice / BasisPrice * 100
    # # #
    # #
    # # # plt.plot(ClosePriceDF)
    # # # plt.plot(FinancialStatementDF['Revenue'])
    # # # plt.show()
    # #
    # # # print(EquityDF)
    # # # print('\n')
    # # # print(RevenueDF)
    # # # print('\n')
    # # # print(OACashFlowDF)
    # # # print('\n')
    # # # print(OADepriciationDF)
    # # # print('\n')
    # # # print(LiabilitiesDF)
    # # # print('\n')
    # # # print(CashDF)
    # #
    # #
    # #
    # # # plt.plot(DF['Liabilities'])
    # # # plt.grid()
    # # # plt.show()
    # return FinancialStatementDF

FinancialIndex()

def CorrelationGraph():
    pass


#주당순이익 계산에서 실패...아마 더 정확한 정보를 구할 수 있다면 가능할지도...