#!/usr/bin/env python

from crabutil import colors
import numpy as numpy

import time
import os
import sys

from CRABAPI.RawCommand import crabCommand
from CRABClient.ClientExceptions import ClientException
from CRABClient.UserUtilities import config, getUsernameFromSiteDB
from httplib import HTTPException
from multiprocessing import Process

color = colors.Paint()

class CrabLibrary():

  def submit(self, config):
        try:
            crabCommand('submit', config = config)
        except HTTPException as hte:
            print "Failed submitting task: %s" % (hte.headers)
        except ClientException as cle:
            print "Failed submitting task: %s" % (cle)

  def doSubmit(self, dataset, mode, era, year, xangle, mass, configfile, filesPerJob, tagname, enable, with_dataset, lfndir, config):

    timestr = time.strftime("%Y-%m-%d_UTC%H-%M-%S")
    parameters = []
    pathname = tagname

    if mode != "NULL":
	parameters.append("Mode="+mode)
        pathname += "_" + mode
     
    if era != "NULL":
        parameters.append("Era="+era)  
        pathname += "_" + era

    if mass != "NULL":
        parameters.append("Mass="+str(mass))
        pathname += "_" + mass

    if xangle != "NULL":
        parameters.append("XAngle="+str(xangle))
        pathname += "_" + xangle

    pathfull = '/store/user/%s/%s_%s/' % (getUsernameFromSiteDB(), pathname, timestr) 

    print "\t" + color.BOLD + "Dataset: " + color.ENDC,
    print "\t" + color.OKGREEN + dataset + color.ENDC

    print "\t" + color.BOLD + "Config file: " + color.ENDC,
    print "\t" + color.OKGREEN + configfile + color.ENDC

    print "\t" + color.BOLD + "TagName: " + color.ENDC,
    print "\t" + color.OKGREEN + tagname + color.ENDC

    print "\t" + color.BOLD + "Era: " + color.ENDC,
    print "\t" + color.OKGREEN + era + color.ENDC

    print "\t" + color.BOLD + "Mode: " + color.ENDC,
    print "\t" + color.OKGREEN + mode + color.ENDC

    print "\t" + color.BOLD + "X-Angle: " + color.ENDC,
    print "\t" + color.OKGREEN + xangle + color.ENDC

    print "\t" + color.BOLD + "Mass: " + color.ENDC,
    print "\t" + color.OKGREEN + mass + color.ENDC

    print "\t" + color.BOLD + "Year: " + color.ENDC,
    print "\t" + color.OKGREEN + str(year) + color.ENDC

    print "\t" + color.BOLD + "Events per job (total of 100 jobs is fixed): " + color.ENDC,
    print "\t" + color.OKGREEN + str(filesPerJob) + color.ENDC

    print "\t" + color.BOLD + "Enable: " + color.ENDC,
    print "\t" + color.OKGREEN + str(enable) + color.ENDC

    print "\t" + color.BOLD + "With Dataset: " + color.ENDC,
    print "\t" + color.OKGREEN + str(with_dataset) + color.ENDC

    print "\t" + color.BOLD + "LFN output dir: " + color.ENDC,
    print "\t" + color.OKGREEN + str(pathfull) + color.ENDC

    if int(with_dataset):
        config.JobType.pluginName = 'Analysis'
        config.Data.inputDataset = dataset
        config.Data.splitting = 'FileBased' # or 'EventBased' or 'LumiBased' or 'Automatic' or 'FileBased'
        config.Data.unitsPerJob = 1
        NJOBS = 100
        #config.Data.totalUnits = -1

    else:
        config.Data.outputPrimaryDataset = pathname
        config.JobType.pluginName = 'PrivateMC'
        config.Data.splitting = 'EventBased' # or 'EventBased' or 'LumiBased' or 'Automatic' or 'FileBased'
        config.Data.unitsPerJob = int(filesPerJob)
        NJOBS = 100
        config.Data.totalUnits = NJOBS * config.Data.unitsPerJob
        print "\t" + color.BOLD + color.HEADER + "-- Submittion without dataset --" + color.ENDC

    config.General.transferLogs = False
    config.General.transferOutputs = True
    config.JobType.maxMemoryMB = 2500
    config.Data.inputDBS = 'phys03'
    config.JobType.allowUndistributedCMSSW = True
    #config.JobType.numCores = 8
    config.Data.publication = True
    config.JobType.psetName = configfile
    config.JobType.outputFiles = ['output.root']
    config.JobType.pyCfgParams = parameters
    config.General.workArea = 'crab_' + pathname + '_' + timestr
    config.General.requestName = pathname + "_" + timestr
    config.Data.outputDatasetTag = pathname + "_" + timestr
    config.Site.storageSite = 'T2_IT_Pisa' #T2_IT_Pisa, T2_CH_CERNBOX
    config.Data.outLFNDirBase = pathfull

    if int(enable):
    	p = Process(target=self.submit, args=(config,))
    	p.start()
    	p.join()
    else:
        print "\t" + color.BOLD + color.HEADER + "-- Submittion not enabled --" + color.ENDC

    print "\n"
