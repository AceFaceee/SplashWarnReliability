import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import rc
from scipy.signal import savgol_filter

rc('mathtext', default='regular')


def splitHeatNo(dataSlice):
    # 将炉号的那组数据输入。比如data['heatNo']。得到一个字典「键：炉次x；值：是一个二元组，（a，b）」；
    # 表示：第x炉次的钢号是从a到b

    # dataFrame data.slice;
    # dictionary; key-int; value-tuple
    heatNoDict = {}
    starters = []
    enders = []
    starters.append(0)

    for i in range(len(data)):
        if (i == 0):
            continue
        if (dataSlice[i] != dataSlice[i - 1]):
            starters.append(i)
            enders.append(i - 1)

    enders.append(len(dataSlice))

    for num in range(len(starters)):
        heatNoDict[num] = (starters[num], enders[num])

    return heatNoDict


def getKey(dict, value):
    # 这是根据字典的值的二元组，找键，不需要调用
    # dict dict;float value;
    # return k

    for k, v in dict.items():
        upper = v[1]
        lower = v[0]
        if value <= upper and value >= lower:
            return k


def disposeO(oSlice):
    newSlice = []
    for each in oSlice:
        newSlice.append(each / 1000)

    return newSlice


def drawTwinSegment(heatNoSlice, lanceHeightSlice, lanceHeightFiltered, coSlice, oSlice, oFiltered, diffSlice, lower, upper, heatNo):
    # 这是画图的函数，根据需求调整里面的参数和代码，目前只能简单画出dataFrame某一区间的折线图
    # void;
    with PdfPages('/Users/klz/Desktop/BaoSteel_Yu/SlagSplash_Analyse/gettyImages.pdf') as pdf:
        ax = plt.figure().add_subplot(111)
        #plt.title("No." + heatNo + "Latent Splash Error Multi-variable Diagram")
        #ax.plot(heatNoSlice[lower:upper], lanceHeightSlice[lower:upper])
        ax.scatter(heatNoSlice[lower:upper], lanceHeightSlice[lower:upper], color='b', label='LanceHeightRaw')
        ax.scatter(heatNoSlice[lower:upper], lanceHeightFiltered[lower:upper], color='r', marker='s', label='LanceHeightFiltered')
        ax2 = ax.twinx()
        #ax2.plot(heatNoSlice[lower:upper], coSlice[lower:upper])
        #ax2.scatter(heatNoSlice[lower:upper], coSlice[lower:upper], color='r', marker='d', label='SmokeAnaCO')
        ax2.scatter(heatNoSlice[lower:upper], oSlice[lower:upper], color='yellow',label='CommonO2Raw')
        ax2.scatter(heatNoSlice[lower:upper], oFiltered[lower:upper], color = 'green', marker = '*', label='CommonO2Filtered')
        #ax2.plot(heatNoSlice[lower:upper], diffSlice[lower:upper], color='g', label='thickSplashDiff')
        # ax2.plot(heatNoSlice[818:1833], standardSlice,color = 'yellow', marker = '*', label = 'warnLine=50')
        ax.legend(loc='upper left')
        ax.grid()
        ax.set_xlabel("timeid")
        ax.set_ylabel(r"LanceHeight(mm)")
        #ax2.set_ylabel(r"SmokeAnaCO (/); CommonO2Flow_new(㎛^3/h)")
        ax2.set_ylabel(r"CommonO2Flow_new(㎛^3/h)")
        ax.set_ylim(1200, 1500)
        ax2.set_ylim(0, 80)
        ax2.legend(loc='upper right')
        plt.show()
        #pdf.savefig(dpi=300)
    # plt.savefig(r'/Users/klz/Desktop/BaoSteel_Yu/SlagSplash_Analyse/No:'+heatNo+'splashWarn.png',dpi=300)


def standardDiff(lower, upper):
    standard = []
    for i in range(upper - lower):
        standard.append(50)

    return standard


def verdictSplash(splashWarnC, target=1):
    # 输入是splashWarnC的那组自己计算的数据，target=1，能查找出喷溅报警的钢号
    # 输出是喷溅报警为1，对应的钢号的列表。
    # 这个列表可以作为其他函数的参数。
    # dataFrame.slice splachWarnC; float target;
    # list;
    splashErrors = []
    for each in range(len(splashWarnC)):
        if splashWarnC[each] == target:
            splashErrors.append(each)
    return splashErrors


def catchDict(heatNoDict, errorsList=None, specificError=None):
    # 输出：data是整张表格，heatNo是Excel记录炉号那一列的表头，heatNoDict是通过heatNoDict方法生成的字典，
    # errorsList是出现喷溅报警的炉号列表。是可变参数，可以不用
    # 取而代之，可以输入具体一个钢号。
    # 这个函数可以查看你想查看的钢号所在炉次，和该炉次的钢号范围。

    # DataFrame data; string heatNo; list errorsList; dict heatNoDict
    # void

    tempIndexes = []
    tempKeys = []
    targetBounds = []

    if errorsList != None:

        for eachError in errorsList:
            tempKey = getKey(heatNoDict, eachError)
            tempKeys.append(tempKey)
        tempKeys = sorted(set(tempKeys))
        for eachKey in tempKeys:
            bounds = (heatNoDict[eachKey][0], heatNoDict[eachKey][1])
            targetBounds.append(bounds)

    # else:
    #    specificKey = getKey(heatNoDict, specificError)
    #    bounds = (heatNoDict[specificKey][0],heatNoDict[specificKey][1])
    #    targetBounds.append(bounds)

    return targetBounds


def SGFilter(dataSlice, windowLength, kValue):
    filtered = savgol_filter(dataSlice,windowLength,kValue)
    return filtered

def readCSV(fileName):
    # 这个就是基本的读数据
    # string fileName;
    # DataFrame;
    data = pd.read_csv(fileName)
    return data


def selfDraw(catches, heatNoSlice, lanceHeightSlice, oSlice, coSlice):
    for eachBound in catches:
        lower = eachBound[0]
        upper = eachBound[1]
        heatNo = heatNoSlice[lower:upper]
        lanceHeight = lanceHeightSlice[lower:upper]
        o = oSlice[lower:upper]
        co = coSlice[lower:upper]
        drawTwinSegment(heatNo, lanceHeight, o, co)


def thickSplashDiff(thickSlice, splashSlice):
    diff = []
    for i in range(len(thickSlice)):
        diff.append((thickSlice[i] - splashSlice[i] + 5000) / 100)
    return diff


def loopDrawCatchesToPDF(catches, heatNoSlice, timeSlice, coSlice, newOSlice, lanceHeightSlice, diffSlice):
    for eachCatch in catches:
        lower = eachCatch[0]
        upper = eachCatch[1]
        heatNo = str(heatNoSlice[eachCatch[0]])
        drawTwinSegment(timeSlice, lanceHeightSlice, coSlice, newOSlice, diffSlice, lower, upper, heatNo)

        plt.close()
    pdf.close()


if __name__ == '__main__':
    data = readCSV(r'/Users/klz/Desktop/BaoSteel_Yu/SlagSplash_Analyse/temp.csv')
    heatNoDict = splitHeatNo(data['___'])

    splashErrors = verdictSplash(data['splashwarn_c'])

    #catches = (catchDict(heatNoDict, errorsList=splashErrors))
    #print(len(catches))
    lanceHeightSlice = data['LanceHeight']
    timeSlice = data['timeid']
    heatNoSlice = data['___']
    oSlice = data['CommonO2Flow_New']
    newOSlice = disposeO(oSlice)
    coSlice = data['SmokeAnaCO']
    oSlice = disposeO(oSlice)
    diffSlice = thickSplashDiff(data['slagthickline'], data['splashline'])

    lanceHeightFiltered = SGFilter(lanceHeightSlice, 153,3)
    oFiltered = SGFilter(oSlice,79,3)
    drawTwinSegment(timeSlice,lanceHeightSlice,lanceHeightFiltered,None,oSlice,oFiltered,None,0,818,None)

    #loopDrawCatchesToPDF(catches, heatNoSlice, timeSlice, coSlice, newOSlice, lanceHeightSlice, diffSlice)

    # standardSlice = standardDiff(14657, 15481)
