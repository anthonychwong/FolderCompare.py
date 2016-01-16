#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import heapq
import sets
import hashlib
import filecmp
import fnmatch
import time
import codecs

import sys 
reload(sys)

defaultSysEncoding = sys.getdefaultencoding()
 
sys.setdefaultencoding('utf8')

###########
#
# File Functions
#
###########

def getDirList(tgtDirPath):
    resultList = []
    for root, dirs, files in os.walk(tgtDirPath):
        
        for f in files:
            fType = os.path.splitext(f)[1]
            resultList.append(str(os.path.relpath(os.path.join(root, f), tgtDirPath)))
    
    return sorted(resultList)

def isExcluded(filePath, masks):
    result = False
    
    for mask in masks:
        if fnmatch.fnmatchcase(filePath, mask):
            result = True
    
    return result        
    
###########
#
# Hash gen
#
###########

def getMD5Hash(filePath):
    md5Hasher = hashlib.md5()    
    block = True
    
    file = open(filePath);
    while block:
        block = file.read(1024)
        md5Hasher.update(block)
    
    file.close()
    
    return md5Hasher.hexdigest()

def getSHA1Hash(filePath):
    sha1Hasher = hashlib.sha1()
    block = True
    
    file = open(filePath);
    while block:
        block = file.read(1024)
        sha1Hasher.update(block)
    
    file.close()

    return sha1Hasher.hexdigest()

###########
#
# Remove Hazardous Characters
#
###########

def cleanString(str2Clean):
    return str2Clean.strip('\r').strip('\n').strip('\t')

###########
#
# Result container
#
###########

class FileCompareResult(object):
    def __init__(self):
        self.commonFilePath = None
        self.commonFolderPath = None
        self.result = ""
        self.fileName = ""

###########
#
# User Input
#
###########

aDir = u"/Path/To/FolderA"
bDir = u"/Path/To/FolderB"
exclude = ".DS_Store|.Parent"
reportName = "CompareReport.csv"

###########
#
# Program main body
#
###########

print(":::: Folder Compare Script [Started] ::::")

excludeLst = exclude.split('|')

aDirList = getDirList(aDir)
bDirList = getDirList(bDir)

firstMergedDirList = set(aDirList) | set(bDirList)
resultList = []

totalNoCmp = len(firstMergedDirList)
countNoCmp = 0.0

startTime = time.strftime("%Y %m %d %H:%M:%S", time.localtime())

print(":::: Compared Results ::::")

for itrCmpFile in firstMergedDirList:
    # Init block, obviously
    aFilePath = os.path.join(aDir, itrCmpFile)
    bFilePath = os.path.join(bDir, itrCmpFile)
        
    cmpResult = FileCompareResult()
    cmpResult.commonFilePath = itrCmpFile
    cmpResult.commonFolderPath = os.path.split(itrCmpFile)[0]
    cmpResult.fileName = os.path.split(itrCmpFile)[1]
    
    if isExcluded(cmpResult.fileName, excludeLst):
        cmpResult.result = "Excluded"
    
    if len(cmpResult.result) == 0:        
        if not os.path.isfile(aFilePath):
            cmpResult.result += "Not found in folder a"
            
        if not os.path.isfile(bFilePath):
            cmpResult.result += "Not found in folder b" 
        
    if len(cmpResult.result) == 0:
        try:
            
            pyCmp = ""
            md5Cmp = ""
            sha1Cmp = ""
            
            if filecmp.cmp(aFilePath, bFilePath, False):
                pyCmp = "Files are same in python file compare."
            else:
                pyCmp = "Files are not same in python file compare."
            
            aFileMD5 = getMD5Hash(aFilePath)
            bFileMD5 = getMD5Hash(bFilePath)
            
            if aFileMD5 == bFileMD5:
                md5Cmp += "MD5 hashs are same with MD5: " + aFileMD5
            else:
                md5Cmp += "MD5 hashs are not same, MD5 in Folder a is {0}, b is {1}".format(aFileMD5, bFileMD5)
            
            aFileSHA1 = getSHA1Hash(aFilePath)
            bFileSHA1 = getSHA1Hash(bFilePath)
            
            if aFileSHA1 == bFileSHA1:
                sha1Cmp += "SHA1 hashs are same with SHA1: " + aFileSHA1
            else:
                sha1Cmp += "SHA1 hashs are not same, SHA1 in Folder a is {0}, b is {1}".format(aFileSHA1, bFileSHA1)
                
            cmpResult.result = "'{}','{}','{}'".format(pyCmp, md5Cmp, sha1Cmp)
            
        except Exception as e:
            cmpResult.result = "Error in compare file: " + type(e).__name__
            print(e)
    
    countNoCmp += 1
    print("[{1}] Progress: {0:.3%} {2}".format(countNoCmp / totalNoCmp, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), itrCmpFile))
    
    resultList.append(cmpResult)

file = open(reportName, "a+")

file.write((u"Compare between aDir {0} and bDir{1}\n".format(aDir.encode('utf8'),bDir.encode('utf8'))).encode('utf8'))
file.write((u"exclude: {0}\n".format(exclude.encode('utf8'))).encode('utf8'))
file.write((u"Comparsion from {0} to {1}\n".format(startTime.encode('utf8'), time.strftime("%Y %m %d %H:%M:%S", time.localtime()).encode('utf8'))).encode('utf8'))

file.write((u"Common File Path,File Name,Folder,Compare Result,MD5 Result,SHA1 Result\n").encode('utf8'))

for result in resultList:
    file.write((u"'{}','{}','{}','{}'\n".format(
    											cleanString(result.commonFilePath).encode('utf8'),
    											cleanString(result.fileName).encode('utf8'),
    											cleanString(result.commonFolderPath).encode('utf8'),
    											result.result.encode('utf8')
    											).encode('utf8')
    			).encode('utf8'))

file.flush()
file.close()

sys.setdefaultencoding(defaultSysEncoding)

print(":::: Folder Compare Script [Finished] ::::")