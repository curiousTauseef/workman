# workman - Workflow Manager
A minimalist, lightweight workflow manager.
Create a Workflow as a YAML file and pass the path as the first positional argument.
Refer to the sample Workflow YAML file below.

#### Things to remember:
- The steps will be executed sequentially in ascending order one at a time.
- There is an option to pass the selective steps to be executed. Refer to the usage section below.
- Every run will get a unique runId in the format: YYYYMMDDHH24MMSS.
- Install the requirements before running the script to avoid errors.

#### Sample Workflow File:
@[:code_block](./wf_sample.yaml)

#### Run Command:
    usage: runner.py [-h] [-l LOGDIR] [-s STEPS] [-v] wfFile

#### Usage:

##### positional arguments:
    - wfFile:
      Workflow yaml file that is to be executed by the runner.

##### optional arguments:
    -h, --help
      Display Help
    -l LOGDIR, --logDir LOGDIR
    Log file directory. Passing this will implicitly enable logging the   output to a file.
      Log file will be in the format: "runnerlog.WorkflowName.runId.log"
    -s STEPS, --steps STEPS
      Steps to execute. If not passed, all the steps will be executed.
      2 Formats supported:
        --> 'ST-EN'. Example: 1-3, 2-5. Both the values need to be a positive   integer number.
        --> 'STEPNO, {STEPNO,}'. Example: 1,3,5. All the step numbers needs to be   positive integer numbers.
      Steps will *always* be executed sequentially in ascending order.
    -v, --verbose
      Increase log verbosity.

#### Requirements:
@[:code_block](./requirements.txt)

##### To install the requirements:
    pip install -r requirements.txt
