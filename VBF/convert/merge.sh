#!/bin/bash 
echo SingleTopSingleTop  Diboson WJets TTbar ZJets ZtoNuNu QCD MET SingleElectron SinglePhoton EWKZJets EWKZtoNuNu EWKWJets VBF_H125 GJets | xargs -n 1 -P 6 python merge.py
