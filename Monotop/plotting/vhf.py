#!/usr/bin/env python

from os import system,getenv
from sys import argv
import argparse

### SET GLOBAL VARIABLES ###
baseDir = getenv('PANDA_FLATDIR')+'/' 
dataDir = baseDir#.replace('0_4','0_4_egfix')
parser = argparse.ArgumentParser(description='plot stuff')
parser.add_argument('--outdir',metavar='outdir',type=str,default=None)
parser.add_argument('--cut',metavar='cut',type=str,default='1==1')
parser.add_argument('--region',metavar='region',type=str,default=None)
parser.add_argument('--tt',metavar='tt',type=str,default='')
args = parser.parse_args()
lumi = 35800.
blind=True
region = args.region
sname = argv[0]

argv=[]
import ROOT as root
root.gROOT.SetBatch()
from PandaCore.Tools.Misc import *
import PandaCore.Tools.Functions
#import PandaAnalysis.Monotop.MonojetSelection as sel
#import PandaAnalysis.Monotop.LooseSelection as sel
#import PandaAnalysis.Monotop.TightSelection as sel
import PandaAnalysis.Monotop.OneFatJetSelection as sel
#import PandaAnalysis.Monotop.TestSelection as sel
from PandaCore.Drawers.plot_utility import *

### DEFINE REGIONS ###

cut = tAND(sel.cuts[args.region],args.cut)

### LOAD PLOTTING UTILITY ###
plot = PlotUtility()
plot.Stack(True)
plot.Ratio(True)
plot.FixRatio(0.2)
if 'qcd' in region:
    plot.FixRatio(1)
plot.SetTDRStyle()
plot.InitLegend()
plot.DrawMCErrors(True)
plot.AddCMSLabel()
plot.cut = cut
plot.SetEvtNum("eventNumber")
plot.SetLumi(lumi/1000)
plot.AddLumiLabel(True)
plot.do_overflow = True
plot.do_underflow = True

lf = 'jet1Flav==0 && jet2Flav==0 && isojet1Flav==0 && isojet2Flav==0'
#lf = 'nHF==0'
hf = tNOT(lf)

weight = sel.weights[region]%lumi
# weight = tTIMES(weight,'sf_sjbtag0MUp*(fj1MaxCSV<0.54)+sf_sjbtag1MUp*(fj1MaxCSV>0.54)')
plot.mc_weight = weight

#PInfo('cut',plot.cut)
#PInfo('weight',plot.mc_weight)

plot.add_systematic('HF uncertainty','0.964*(%s) + 1.2*(%s)'%(lf,hf),'1.036*(%s) + 0.8*(%s)'%(lf,hf),root.kRed+2)
plot.add_systematic('b-tag SF unc',{'sf_sjbtag0':'sf_sjbtag0BUp','sf_sjbtag1':'sf_sjbtag1BUp'},
                                   {'sf_sjbtag0':'sf_sjbtag0BDown','sf_sjbtag1':'sf_sjbtag1BDown'},root.kBlue+2)
plot.add_systematic('mis-tag SF unc',{'sf_sjbtag0':'sf_sjbtag0MUp','sf_sjbtag1':'sf_sjbtag1MUp'},
                                     {'sf_sjbtag0':'sf_sjbtag0MDown','sf_sjbtag1':'sf_sjbtag1MDown'},root.kGreen+2)

#plot.add_systematic('PDF','pdfUp','pdfDown',root.kBlue+2)

### DEFINE PROCESSES ###
zlf          = Process('Z+LF',root.kZjets); zlf.additional_cut = lf
zhf          = Process('Z+HF',root.kExtra1); zhf.additional_cut = hf
wlf          = Process('W+LF',root.kWjets); wlf.additional_cut = lf
whf          = Process('W+HF',root.kExtra2); whf.additional_cut = hf
diboson       = Process('Diboson',root.kDiboson)
ttbar         = Process('t#bar{t}',root.kTTbar)
ttg           = Process('t#bar{t}#gamma',root.kTTbar)
singletop     = Process('Single t',root.kST)
singletopg    = Process('t#gamma',root.kST)
qcd           = Process("QCD",root.kQCD)
gjets         = Process('#gamma+jets',root.kGjets)
data          = Process("Data",root.kData)
signal        = Process('m_{V}=1.75 TeV, m_{#chi}=1 GeV',root.kSignal)
#processes = [qcd,diboson,singletop,ttbar,wewk,zewk,wjets,zjets]
processes = [qcd,diboson,singletop,wlf,whf,ttbar,zhf,zlf]
#processes = [qcd,diboson,zhf]

### ASSIGN FILES TO PROCESSES ###
for z in [zlf,zhf]:
    if 'signal' in args.region:
        z.add_file(baseDir+'ZtoNuNu.root')
    else:
        z.add_file(baseDir+'ZJets_hf.root')
for w in [wlf,whf]:
    w.add_file(baseDir+'WJets_hf.root')
diboson.add_file(baseDir+'Diboson.root')
ttbar.add_file(baseDir+'TTbar%s.root'%(args.tt));
singletop.add_file(baseDir+'SingleTop.root')
ttg.add_file(baseDir+'TTbar_Photon.root');
singletopg.add_file(baseDir+'SingleTop_tG.root')
if 'pho' in region:
    #processes = [qcd,singletopg,ttg,gjets]
    processes = [qcd,gjets]
    gjets.add_file(baseDir+'GJets.root')
    qcd.add_file(baseDir+'SinglePhoton.root')
    qcd.additional_cut = sel.triggers['pho']
    qcd.use_common_weight = False
    qcd.additional_weight = 'sf_phoPurity'
else:
    qcd.add_file(baseDir+'QCD.root')

if any([x in region for x in ['signal','muon','qcd']]):
    data.additional_cut = sel.triggers['met']
    data.add_file(dataDir+'MET.root')
    lep='#mu'
elif 'electron' in region:
    if 'di' in region:
        data.additional_cut = tOR(sel.triggers['ele'],sel.triggers['pho'])
    else:
        data.additional_cut = sel.triggers['ele']
    data.add_file(dataDir+'SingleElectron.root')
    lep='e'
elif region=='photon':
    data.additional_cut = sel.triggers['pho']
    data.add_file(dataDir+'SinglePhoton.root')


processes.append(data)

for p in processes:
    plot.add_process(p)

recoilBins = [250,280,310,350,400,450,600,1000]
nRecoilBins = len(recoilBins)-1

### CHOOSE DISTRIBUTIONS, LABELS ###
if 'signal' in region or 'qcd' in region:
    recoil=VDistribution("pfmet",recoilBins,"PF MET [GeV]","Events/GeV")
elif any([x in region for x in ['singlemuonw','singleelectronw','singlemuontop','singleelectrontop','singlemuon','singleelectron']]):
    recoil=VDistribution("pfUWmag",recoilBins,"PF U(%s) [GeV]"%(lep),"Events/GeV")
    plot.add_distribution(FDistribution('looseLep1Pt',0,1000,20,'Leading %s p_{T} [GeV]'%lep,'Events/40 GeV'))
    plot.add_distribution(FDistribution('looseLep1Eta',-2.5,2.5,20,'Leading %s #eta'%lep,'Events/bin'))
elif any([x in region for x in ['dielectron','dimuon']]):
    recoil=VDistribution("pfUZmag",recoilBins,"PF U(%s%s) [GeV]"%(lep,lep),"Events/GeV")
    plot.add_distribution(FDistribution('diLepMass',60,120,20,'m_{ll} [GeV]','Events/3 GeV'))
    plot.add_distribution(FDistribution('looseLep1Pt',0,1000,20,'Leading %s p_{T} [GeV]'%lep,'Events/40 GeV'))
    plot.add_distribution(FDistribution('looseLep1Eta',-2.5,2.5,20,'Leading %s #eta'%lep,'Events/bin'))
    plot.add_distribution(FDistribution('looseLep2Pt',0,1000,20,'Subleading %s p_{T} [GeV]'%lep,'Events/40 GeV'))
    plot.add_distribution(FDistribution('looseLep2Eta',-2.5,2.5,20,'Subleading %s #eta'%lep,'Events/bin'))
elif region=='photon':
    recoil=VDistribution("pfUAmag",recoilBins,"PF U(#gamma) [GeV]","Events/GeV")
    plot.add_distribution(FDistribution('loosePho1Pt',0,1000,20,'Leading #gamma p_{T} [GeV]','Events/40 GeV'))
    plot.add_distribution(FDistribution('loosePho1Eta',-2.5,2.5,20,'Leading #gamma #eta','Events/bin'))

#recoil.calc_chi2 = True
plot.add_distribution(recoil)

btagbins = [0,0.54,1]

plot.add_distribution(VDistribution('fj1MaxCSV',btagbins,'fatjet max CSV','Events'))
plot.add_distribution(VDistribution('jet1CSV',btagbins,'jet 1 CSV','Events',filename='jet1CSV'))
plot.add_distribution(VDistribution('isojet1CSV',btagbins,'isojet 1 CSV','Events',filename='isojet1CSV'))
plot.add_distribution(FDistribution('jetNBtags',-0.5,1.5,2,'N_{b-tag} jets','Events'))
plot.add_distribution(FDistribution('isojetNBtags',-0.5,1.5,2,'N_{b-tag} isojets','Events'))

plot.add_distribution(FDistribution('fj1Pt',200,1000,20,'fatjet p_{T} [GeV]','Events'))
# plot.add_distribution(FDistribution('fj1MaxCSV',0,1,20,'fatjet max CSV','Events'))
# plot.add_distribution(FDistribution('jet1CSV',0,1,20,'jet 1 CSV','Events',filename='jet1CSV'))
# plot.add_distribution(FDistribution('isojet1CSV',0,1,20,'isojet 1 CSV','Events',filename='isojet1CSV'))
plot.add_distribution(FDistribution("1",0,2,1,"dummy","dummy"))

### DRAW AND CATALOGUE ###
plot.draw_all(args.outdir+'/'+region+'_')
