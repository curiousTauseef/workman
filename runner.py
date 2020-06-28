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

def runSubProcess(command):
  OUT=subprocess.run(command, shell=True, capture_output=True, encoding="utf-8")
  if OUT.returncode:
    if args.verbose:
      raise Exception(OUT.stdout + "\n" + OUT.stderr)
    else:
      raise Exception(OUT.stdout)
  if args.verbose:
    print(OUT.stdout)

def parseCmd():
  global args
  parser = ArgumentParser()
  parser.add_argument("wfFile", type=str, help="Workflow yaml file that is to be executed by the runner.")
  parser.add_argument("-l", "--logDir", type=str, help="Log file directory. Passing this will implicitly enable logging the output to a file.")
  parser.add_argument("-v", "--verbose", action="store_true", help="Increase error log verbosity.")
  args = parser.parse_args()

def initialize():
  global wf
  global conf
  if args.verbose:
    sys.tracebacklimit=1000
  
  if not path.isfile(args.wfFile):
    raise Exception("Workflow yaml file [" + args.wfFile +"] is not accessible.")
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
      raise Exception("[" + args.logDir +"] does not exist or is not a directory.")
    else:
      setLogFile(args.logDir + "/" + conf["logFileName"])

def executeWorkflow():
  global status
  for task in wf["Tasks"]:
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
  status["WorkflowName"] = wf["WorkflowName"]
  status["Description"] = wf["Description"]
  status["runId"] = conf["runId"]
  status["Tasks"] = []
  status["StartTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  executeWorkflow()
  status["EndTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  print(yaml.dump(status))
  print("Execution completed Successfully...")
