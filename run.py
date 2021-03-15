#!/bin/python3
# -*- coding: utf-8 -*- 
import os
import json
import time
import argparse
import configparser
import datetime
import shutil
import re
import subprocess

################### argparser #######################
#buildfile = GEM 5의 빌드파일
#configfile = GEM 5의 구성파일
#optionfile = GEM 5실행시 옵션값파일

parser = argparse.ArgumentParser(description='GEM5 script')
parser.add_argument('-f', '--optionfile', action='store', dest='optionfile', help='ALL Option file')
parser.add_argument('-d', '--desc', action='store', dest='desc', help='GEM5 Description')
parser.add_argument('-i', '--gem5id', action='store', dest='gem5id', help='specify a simulation id for re-run')
parser.add_argument('-w', '--waittime', action='store', dest='waittime', help='specify a wiat time before running simulation')

args = parser.parse_args()


config = configparser.ConfigParser()
config.optionxform = str
config.read(args.optionfile)
#########################################################

date=datetime.datetime.now().strftime("%m-%d-%y")
time_h_m=datetime.datetime.now().strftime("%H:%M")

gem5_id="";

if args.gem5id == None:
    gem5_id=str(int(time.time()*1000))
else:
    gem5_id=str(args.gem5id)

wait_time=args.waittime;

########Setup simulation parameters ######################
PWD = os.getcwd()
OUTPUT_DIR=PWD+"/out/"+date;
MAXMEM = 4*1024

########### Create Output directory #######################
if os.path.exists(OUTPUT_DIR)==False:
    print("Create " + OUTPUT_DIR)
    os.mkdir(OUTPUT_DIR)
    os.system("chmod g+w " + OUTPUT_DIR)

shutil.copy2(args.optionfile, OUTPUT_DIR+"/"+str(gem5_id)+"-"+str(args.optionfile))


################벤치마크 금회차 설정########################

history_file=PWD+"/history.json";
description=""
if args.gem5id == None:
    print("\nBatch simulation");
    print("Date: " +date);
    print("Time: " +time_h_m);
    print("Simulaiton ID: "+str(gem5_id));
    print("Simulation History File: "+history_file);

    if args.desc == None:
        description=input("Description?: ");
    else:
        description=args.desc
    #print(description)

    print("Output directory: "+OUTPUT_DIR);
else:
    print("rerun gem5id: "+str(gem5_id))


################빌드 및 구성 파일 옵션 설정 ####################

def AddOption(tag) : 
    parm=""
    options=config.options(tag)
    for option_name in options:
        option_value = config.get(tag,option_name)
        if option_value == "" : 
            parm = parm + " "+ option_name
        else : 
            parm = parm + " "+ option_name + "=" + option_value
    #print(tag+parm)
    return parm

gem5_build_option = ""
gem5_config_option = ""
output_post_fix = ""

#gem5_build_option = AddOption("BUILDOPT")
gem5_config_option = AddOption("CONFIGOPT")

gem5_build_option = "--outdir=" + OUTPUT_DIR

output_post_fix = gem5_id + '.'

gem5_build_file=config.get("TRACE","BUILDFILE").split('\n')
gem5_config_file=config.get("TRACE","CONFIGFILE").split('\n')

#print(gem5_build_file[0])
#print(gem5_config_file[0])

########################## 실행 #############################

def RunBench(tag) : 
    bench_pwd=config.options(tag)
    for i in range(len(bench_pwd)) : 
        cmd=""
        temp = ""
        bench_option =config.get(tag,bench_pwd[i])
        temp = gem5_build_option + " --stats-file="+ gem5_id +"-"+str(bench_pwd[i])
        print("temp = "+ temp)
        if bench_option == "" : 
            cmd = gem5_build_file[0] + " " \
            + temp + " " \
            + gem5_config_file[0] + " " \
            + gem5_config_option + " " \
            + "--cmd=" + bench_pwd[i]
        else : 
            cmd = gem5_build_file[0] + " " \
            + temp + " " \
            + gem5_config_file[0] + " " \
            + gem5_config_option + " " \
            + "--cmd=" + bench_pwd[i] + " "\
            + '--options="' + bench_option + '"' 
        #os.system(cmd)
        wd = os.getcwd()
        os.chdir("/disk1/ryotta205/benchmark/SPEC_2006/"+bench_pwd[i])
        subprocess.call(cmd,shell=True)
        os.chdir(wd)
        time.sleep(5)
    


RunBench("BENCHMARK")

###############history 추가##################
data= {}
if os.path.exists(history_file)==True:
    with open(history_file,'r') as json_file:
         data=json.load(json_file)
else:
    data['log']=[]

data['log'].append({
    'id': gem5_id,
    'date': date,
    'time': time_h_m,
    #'benchmarks':all_benchmark,
    #'options':all_option,
    'description':description
    })
with open(history_file,"w") as json_file:
    json.dump(data, json_file, indent="\t")