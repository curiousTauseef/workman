#!/usr/bin/env python
import sys, yaml, subprocess
from argparse import Namespace, ArgumentParser
from os import path
from datetime import datetime
from _logger import setLogFile
sys.tracebacklimit=0

args=Namespace()
wf={}
conf={}
status={}

def exitWithError(message):
  print(message)
  print("Exiting with error...")
  exit(99)

def getSteps():
  global conf
  _steps=[]
  
  if args.steps:
    if "-" in args.steps:
      print("Steps passed as ST-EN")
      s = args.steps.split("-")
      if (len(s) != 2):
        exitWithError("Only 2 values are supported when using ST-EN format.")
      else:
        try:
          _FROM=int(s[0])
          _TO=int(s[1])
        except ValueError:
          exitWithError("Non numeric step number passed. Please check.")
      _steps=list(range(_FROM, _TO + 1))
    elif "," in args.steps:
      print("Steps passed as list")
      for s in args.steps.split(","):
        if s.strip() != "":
          try:
            _steps.append(int(s))
          except ValueError:
            exitWithError("Non numeric step number passed. Please check.")
      _steps = list(dict.fromkeys(_steps))
      _steps.sort()
    else:
      exitWithError("Incorrect format of steps. Check usage for supported formats.")
  else:
    _FROM=1
    _TO=len(wf["Tasks"]) + 1
    _steps=list(range(_FROM, _TO))
  
  conf["steps"]=_steps

def runSubProcess(command):
  OUT=subprocess.run(command, shell=True, capture_output=True, encoding="utf-8")
  if OUT.returncode:
    if args.verbose:
      exitWithError(OUT.stdout + "\n" + OUT.stderr)
    else:
      exitWithError(OUT.stdout)
  if args.verbose:
    print(OUT.stdout)

def parseCmd():
  global args
  parser = ArgumentParser()
  parser.add_argument("wfFile", type=str, help="Workflow yaml file that is to be executed by the runner.")
  parser.add_argument("-l", "--logDir", type=str, help="Log file directory. Passing this will implicitly enable logging the output to a file.")
  parser.add_argument("-s", "--steps", type=str, help="Steps to execute. 2 Formats supported: 'ST-EN', 'STEPNO, {STEPNO,}'.")
  parser.add_argument("-v", "--verbose", action="store_true", help="Increase log verbosity.")
  args = parser.parse_args()

def initialize():
  global wf
  global conf
  if args.verbose:
    sys.tracebacklimit=1000
  
  if not path.isfile(args.wfFile):
    exitWithError("Workflow yaml file [" + args.wfFile +"] is not accessible.")
  else:
    print("Parsing [" + args.wfFile + "] and validating format.")
    runSubProcess("pykwalify -d " + args.wfFile + " -s WF_Schema.yaml")
    print("Schema validation successful. Loading Workflow.")
    wf = yaml.load(open(args.wfFile), Loader=yaml.FullLoader)
    print("Workflow loaded successfully.")
  
  print("Getting new Run ID.")
  conf["runId"] = datetime.now().strftime("%Y%m%d%H%M%S")
  print("Run ID = " + conf["runId"])

  if args.logDir:
    print("Initializing Log File.")
    conf["logFileName"] = "runnerlog." + wf["WorkflowName"] + "." + conf["runId"] + ".log"
    if not path.isdir(args.logDir):
      exitWithError("[" + args.logDir +"] does not exist or is not a directory.")
    else:
      setLogFile(args.logDir + "/" + conf["logFileName"])

def executeWorkflow():
  global status
  i=0
  for task in wf["Tasks"]:
    i+=1
    if i in conf["steps"]:
      _task=task.copy()
      print("Executing task : " + task["TaskName"] + " : " + task["RunCommand"])
      _task["StartTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      runSubProcess(task["RunCommand"])
      _task["EndTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      status["Tasks"].append(_task)

if __name__ == "__main__":
  parseCmd()
  initialize()
  print("Starting execution of Workflow '{wfname}' with runid '{runid}'...".format(wfname=wf["WorkflowName"], runid=conf["runId"]))
  if args.steps:
    print("Steps specified for execution: '{steps}'...".format(steps=args.steps))
  getSteps()
  status["WorkflowName"] = wf["WorkflowName"]
  status["Description"] = wf["Description"]
  status["runId"] = conf["runId"]
  status["Tasks"] = []
  status["StartTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  executeWorkflow()
  status["EndTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  print(yaml.dump(status))
  print("Execution completed Successfully...")
else:
  exitWithError("This is not a module. Please check the usage...")
