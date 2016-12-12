#!/bin/bash

export PANDA="${CMSSW_BASE}/src/PandaAnalysis"
export PANDA_PROD="${EOS2}/pandaprod/v_8022_2_snarayan/:${EOS2}/pandaprod/v_8022_2_bmaier/" # can have multiple paths, separated by : 
export PANDA_CFG="http://snarayan.web.cern.ch/snarayan/eoscatalog/20161210.cfg"
export PANDA_FLATDIR="${HOME}/home000/store/panda/v_8020_2_2/"

#export SUBMIT_CFG="test"
export SUBMIT_CFG="prod"
export SUBMIT_LOGDIR="/data/t3serv014/snarayan/condor/logs/"
export SUBMIT_WORKDIR="/data/t3serv014/snarayan/condor/work/"
export SUBMIT_OUTDIR="/mnt/hadoop/cms/store/user/snarayan/panda/v_8020_2_2/batch/"
#export SUBMIT_TMPL="skim_csv_tmpl.py"
export SUBMIT_TMPL="skim_tmpl.py"

export PRIVATE_LOGDIR="${HOME}/cms/logs/monotop_private_panda/"
export PRIVATE_PRODDIR="${HOME}/cms/hist/monotop_private_panda/"
export PRIVATE_CFGDIR="${HOME}/cms/condor/monotop_private_panda/"
