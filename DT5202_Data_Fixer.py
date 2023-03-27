# Author: S. Jia
# Institute: Niels Bohr Institute
# Date: 2023-03-25

import numpy as np
import argparse
import matplotlib.pyplot as plt
from collections import Counter
import time

parser = argparse.ArgumentParser(description="Data fixer for TrgID and TS errors in DT5202 data.")
parser.add_argument("--input", type=str, required=True, help="Input file path.")
parser.add_argument("--output", type=str, required=False, help="Output file path.")
args = parser.parse_args()
enable_output = False
output_file = 'output.txt'
input_file = args.input
if args.output is not None:
    output_file = args.output
    enable_output = True

print("====================================================")   
print("==== Welcome to the DT5202 Data Fixer ==============")
print("==== version 1.0                      ==============")
print("==== by S. Jia                        ==============")
print("==== Niels Bohr Institute, 2023       ==============")
print("====================================================")
print(f"info:  input  file: {input_file}")
if enable_output:
    print(f"info:  output file: {output_file}")
else:
    print(f"info:  output file: disabled")

# Read data
try:
    dataFile = open(input_file, "r")
    print(f"info:  data loaded from {input_file}")
except:
    print(f"error: cannot load data from {input_file}")
    exit()

print(f"step:  collecting line number of file...")
lineCnt = sum(1 for line in dataFile)
# transfer according to the unit
if lineCnt < 1024:
    lineCntStr = str(lineCnt) + ' lines'
elif lineCnt < 1024 * 1024:
    lineCntStr = str(round(lineCnt / 1024, 2)) + ' K lines'
elif lineCnt < 1024 * 1024 * 1024:
    lineCntStr = str(round(lineCnt / 1024 / 1024, 2)) + ' M lines'
else:
    lineCntStr = str(round(lineCnt / 1024 / 1024 / 1024, 2)) + ' G lines'
print(f"info:  {lineCntStr} in the data file")

fileSize = dataFile.tell()
# transfer according to the unit
if fileSize < 1024:
    fileSizeStr = str(fileSize) + ' B'
elif fileSize < 1024 * 1024:
    fileSizeStr = str(round(fileSize / 1024, 2)) + ' KB'
elif fileSize < 1024 * 1024 * 1024:
    fileSizeStr = str(round(fileSize / 1024 / 1024, 2)) + ' MB'
else:
    fileSizeStr = str(round(fileSize / 1024 / 1024 / 1024, 2)) + ' GB'
print(f"info:  {fileSizeStr} in the data file")

lineDivider = int(lineCnt / 10)

print(f"step:  reading data...")
blockDevider = '----------------------------------'
blockBoardNumHeader = 'Board'
blockTSHeader       = 'TS'
blockTrgIDHeader    = 'TrgID'
blockCHHeader       = 'CH'

linePos         = 0
headRead        = False
headFound       = False
lastTrgID       = 0
currentTrgID    = 0
currentChnCnt   = 0

raw_boardNum_array      = []
raw_trgID_array         = []
raw_TS_array            = []
blockIntact_array       = []
raw_chnCnt_array        = []
raw_lineChVal_array     = []
raw_ChVal_block_array   = []
raw_abnormalChValCnt_array = []
dataFile.seek(0)
start_time = time.time()

currentTrgID_found      = False
currentTS_found         = False
currentBoardNum_found   = False
currentCH_found         = False
currentAbnormalChnCnt   = 0
currentChnCnt           = 0
currentFrameCnt         = 0

# TODO: remove line limit in real use
# maxLine2Read = 4000000
maxLine2Read = 0
for line in dataFile:
    linePos += 1
    # show progress
    if linePos % lineDivider == 0:
        # print progress with percentage
        print('prog: ', round(linePos / lineCnt * 100), '%')
    # *------------------------------------------------------------*
    if not headRead:
        if not headFound:
            if line == '//************************************************\n':
                headFound = True
                # print("// == File Head Info ================================")
        else:
            if line == '//************************************************\n':
                headRead = True
                # print("// == File Head Ends ================================")
            else:
                print('head:  ' + line, end='')
        continue
    # *------------------------------------------------------------*
    if blockBoardNumHeader in line:
        currentBoardNum         = int(line.split()[1])
        currentBoardNum_found   = True
        raw_boardNum_array.append(currentBoardNum)
    elif blockTrgIDHeader in line:
        currentTrgID            = int(line.split(sep='=')[1])
        currentTrgID_found      = True
        raw_trgID_array.append(currentTrgID)
    elif blockTSHeader in line:
        currentTS               = float((line.split(sep='=')[1]).split()[0])
        currentTS_found         = True
        raw_TS_array.append(currentTS)
    elif blockCHHeader in line:
        currentCH_found         = True
    elif blockDevider in line:
        currentFrameCnt += 1
        if currentTrgID_found and currentTS_found and currentBoardNum_found and currentCH_found:
            currentTrgID_found      = False
            currentTS_found         = False
            currentBoardNum_found   = False
            currentCH_found         = False
            raw_chnCnt_array.append(currentChnCnt)
            currentChnCnt = 0
            blockIntact_array.append(True)
            raw_abnormalChValCnt_array.append(currentAbnormalChnCnt)
            currentAbnormalChnCnt = 0

        else:
            print(f"error: data frame incomplete at line {linePos}")
            print(f"error: TrgID found: {currentTrgID_found}")
            print(f"error: TS found: {currentTS_found}")
            print(f"error: BoardNum found: {currentBoardNum_found}")
            print(f"error: CH found: {currentCH_found}")
            raw_chnCnt_array.append(currentChnCnt)
            currentChnCnt = 0
            blockIntact_array.append(False)
            raw_abnormalChValCnt_array.append(currentAbnormalChnCnt)
            currentAbnormalChnCnt = 0
    elif currentCH_found:
        currentChnCnt += 1
        try:
            currentLineChnVal = int(line.split()[1])
            raw_lineChVal_array.append(currentLineChnVal)
            raw_ChVal_block_array.append(currentFrameCnt)
            if currentLineChnVal > 4095 or currentLineChnVal <= 0:
                currentAbnormalChnCnt += 1
        except:
            print(f"error: data frame incomplete at line {linePos}")
    if linePos >= maxLine2Read and maxLine2Read != 0:
        break

if currentTrgID_found or currentTS_found or currentBoardNum_found or currentCH_found:
    print(f"error: last data frame incomplete at line {linePos}")
    print(f"error: TrgID found: {currentTrgID_found}")
    print(f"error: TS found: {currentTS_found}")
    print(f"error: BoardNum found: {currentBoardNum_found}")
    print(f"error: CH found: {currentCH_found}")
    raw_chnCnt_array.append(currentChnCnt)
    currentChnCnt = 0
    blockIntact_array.append(False)
    raw_abnormalChValCnt_array.append(currentAbnormalChnCnt)
    currentAbnormalChnCnt = 0

dataFile.close()

elapsed_time = round(time.time() - start_time, 2)
print(f"info:  data read in {elapsed_time} seconds")
print("--------------------------------------------")

# * === End of file reading ===

intactBlockCnt = 0
for i in range(len(blockIntact_array)):
    if blockIntact_array[i]:
        intactBlockCnt += 1
print(f"info:  {intactBlockCnt} / {len(blockIntact_array)} frames intact")

zeroCHInfoCnt = 0
for i in range(len(raw_chnCnt_array)):
    if raw_chnCnt_array[i] == 0:
        zeroCHInfoCnt += 1
print(f"info:  {zeroCHInfoCnt} / {len(raw_chnCnt_array)} frames with zero CH value")

abnormalChValCnt = 0
for i in range(len(raw_abnormalChValCnt_array)):
    if raw_abnormalChValCnt_array[i] != 0:
        abnormalChValCnt += 1
print(f"info:  {abnormalChValCnt} / {len(raw_abnormalChValCnt_array)} frames with abnormal CH value")

element_cnt_TrgID       = Counter(raw_trgID_array)
element_unique_TrgID    = list(element_cnt_TrgID.keys())

print(f"info:  {len(raw_trgID_array)} total TrgIDs, {len(element_unique_TrgID)} unique")

num_showed_trgID_once   = 0
num_showed_trgID_twice  = 0
num_showed_trgID_three  = 0
num_showed_trgID_more   = 0

for i in range(len(element_unique_TrgID)):
    if element_cnt_TrgID[element_unique_TrgID[i]] == 1:
        num_showed_trgID_once += 1
    elif element_cnt_TrgID[element_unique_TrgID[i]] == 2:
        num_showed_trgID_twice += 1
    elif element_cnt_TrgID[element_unique_TrgID[i]] == 3:
        num_showed_trgID_three += 1
    else:
        num_showed_trgID_more += 1

print(f"info:  {num_showed_trgID_once} TrgIDs showed once")
print(f"info:  {num_showed_trgID_twice} TrgIDs showed twice")
print(f"info:  {num_showed_trgID_three} TrgIDs showed three times")
print(f"info:  {num_showed_trgID_more} TrgIDs showed more than three times")

# ! TrgID outlier filter using diff
TrgID_diff_array = np.diff(raw_trgID_array)
# find diff > 1000
TrgID_outlier_index_diff = np.where(TrgID_diff_array > 1000000)
# add 1 to the index to get the outlier index
TrgID_outlier_index_diff = TrgID_outlier_index_diff[0] + 1
if len(TrgID_outlier_index_diff) > 0:
    print(f"info:  TrgID outliers index list (diff method):")
    print(f"info:  {TrgID_outlier_index_diff}")
else:
    print(f"info:  no TrgID outliers found (diff method)")

# ! TrgID outlier filter using IQR
# create np array for TrgID
TrgID_float_array = np.array(raw_trgID_array)
Q1 = np.percentile(TrgID_float_array, 25)
Q3 = np.percentile(TrgID_float_array, 75)
IQR = Q3 - Q1
lower_bound = Q1 - (1.5 * IQR)
upper_bound = Q3 + (1.5 * IQR)
filtered_data = TrgID_float_array[(TrgID_float_array > lower_bound) & (TrgID_float_array < upper_bound)]
TrgID_outlier_index_IQR = np.array(np.where((TrgID_float_array > upper_bound) | (TrgID_float_array < lower_bound))[-1])
if len(filtered_data) != len(TrgID_float_array):
    print(f"info:  TrgID outliers index list (IQR method):")
    print(f"info:  {TrgID_outlier_index_IQR}")
else:
    print(f"info:  no TrgID outliers found (IQR method)")

# ! TS outlier filter using diff
TS_diff_array = np.diff(raw_TS_array)
# find diff > 1000
TS_outlier_index_diff = np.where(TS_diff_array > 1000000000)
# add 1 to the index to get the outlier index
TS_outlier_index_diff = TS_outlier_index_diff[0] + 1
if len(TS_outlier_index_diff) > 0:
    print(f"info:  TS outliers index list (diff method):")
    print(f"info:  {TS_outlier_index_diff}")
else:
    print(f"info:  no TS outliers found (diff method)")

# ! TS outlier filter using IQR
# create np array for TS
TS_float_array = np.array(raw_TS_array)
Q1 = np.percentile(TS_float_array, 25)
Q3 = np.percentile(TS_float_array, 75)
IQR = Q3 - Q1
lower_bound = Q1 - (1.5 * IQR)
upper_bound = Q3 + (1.5 * IQR)
filtered_data = TS_float_array[(TS_float_array > lower_bound) & (TS_float_array < upper_bound)]
TS_outlier_index_IQR = np.array(np.where((TS_float_array > upper_bound) | (TS_float_array < lower_bound))[-1])
if len(filtered_data) != len(TS_float_array):
    print(f"info:  TS outliers index list (IQR method):")
    print(f"info:  {TS_outlier_index_IQR}")
else:
    print(f"info:  no TS outliers found (IQR method)")


# * Filter out the incomplete data frames
# * =====================================================================
print(f"step:  generating valid frame list...")
frameValid_array = []
for i in range(len(blockIntact_array)):
    if blockIntact_array[i]:
        if raw_abnormalChValCnt_array[i] == 0 and ~ np.any(np.isin(TS_outlier_index_IQR, i)) and ~ np.any(np.isin(TrgID_outlier_index_IQR, i)):
            frameValid_array.append(True)
        else:
            frameValid_array.append(False)
    else:
        frameValid_array.append(False)

intact_boardNum_array = []
intact_trgID_array = []
intact_TS_array = []
for i in range(len(blockIntact_array)):
    if frameValid_array[i]:
        intact_boardNum_array.append(raw_boardNum_array[i])
        intact_trgID_array.append(raw_trgID_array[i])
        intact_TS_array.append(raw_TS_array[i])
# * =====================================================================

# Summary of the data file
print("====================================================")
print("==== Summary of the data file ======================")
print("====================================================")
if headFound is False:
    print(f"warn:  (>_<) file head not found")

if headRead is False:
    print(f"warn:  (>_<) file head not read")

isAllIntact = intactBlockCnt == len(blockIntact_array)
if isAllIntact:
    print(f"pass:  (^.^) all data frames intact")
else:
    print(f"warn:  (>_<) {intactBlockCnt} frames intact, {len(blockIntact_array) - intactBlockCnt} frames corrupted")

if abnormalChValCnt == 0:
    print(f"pass:  (^.^) all CH values are whithin range")
else:
    print(f"warn:  (>_<) {abnormalChValCnt} frames with abnormal CH values found")

if len(TS_outlier_index_IQR) == 0:
    print(f"pass:  (^.^) no TS outliers found")
else:
    print(f"warn:  (>_<) {len(TS_outlier_index_IQR)} TS outliers found")

if len(TrgID_outlier_index_IQR) == 0:
    print(f"pass:  (^.^) no TrgID outliers found")
else:
    print(f"warn:  (>_<) {len(TrgID_outlier_index_IQR)} TrgID outliers found")
print("====================================================")

# * Copy data to the output file selectively
# * =====================================================================
if enable_output:
# Open input and output files
    start_time = time.time()
    print(f"step:  generating output file...")
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        # Iterate over lines in input file and the valid flag array simultaneously
        infile_linePos  = 0
        outfile_linePos = 0
        current_frameNum= 0
        headRead        = False
        headFound       = False
        for line in infile:
            if infile_linePos % lineDivider == 0:
                # print progress with percentage
                print('prog: ', round(infile_linePos / lineCnt * 100), '%')
            # *------------------------------------------------------------*
            if not headRead:
                outfile.write(line)
                if not headFound:
                    if line == '//************************************************\n':
                        outfile.write('// This is fixed data file generated by DT5202 Data Fixer \n')
                        headFound = True
                        # print("// == File Head Info ================================")
                else:
                    if line == '//************************************************\n':
                        headRead = True
                        # print("// == File Head Ends ================================")
                    else:
                        print('head:  ' + line, end='')
                infile_linePos += 1
                continue
            # *------------------------------------------------------------*
            # If the current line is marked as valid, write it to the output file

            if frameValid_array[current_frameNum] and headRead:
                outfile.write(line)
                outfile_linePos += 1
            if blockDevider in line:
                current_frameNum += 1
            infile_linePos += 1
        infile.close()
        outfile.close()
        elapsed_time = round(time.time() - start_time, 2)
        print(f"info:  output file generated in {elapsed_time} seconds")

print("====================================================")
print("==== Data Fixer Ends ===============================")
print("====================================================")
    

