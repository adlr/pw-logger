import subprocess
from datetime import datetime
import json
#from jycm.jycm import YouchamaJsonDiffer
from deepdiff import DeepDiff
from pathlib import Path

# Define the command to run as a subprocess
command = ["pw-dump", "-m"]

# Start the subprocess and set up stdout as a pipe
process = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True)

cache: dict[int, dict] = {}
outdir = Path('out')

def write(filename, obj, shouldLog=False):
    if shouldLog:
        print(f"{filename}")
    with open(outdir / filename, "w") as f:
        f.write(obj if isinstance(obj, str) else json.dumps(obj))

def prettyObj(obj) -> str:
    if obj["type"] == "PipeWire:Interface:Device":
        return f"Device {obj['info']['props'].get('device.alias', '')} {obj['info']['props']['device.name']}"
    if obj["type"] == "PipeWire:Interface:Port":
        return f"Port {obj['info']['props'].get('port.alias', '')} {obj['info']['props']['port.name']}"
    return obj["type"]

def handleObject(when: datetime, obj):
    id = obj["id"]
    whenstr = when.strftime("%Y-%m-%d-%H-%M-%S.%f")
    if "info" in obj and obj["info"] == None:
        # Deleted
        write(f"{whenstr}-@{id}-DELETED", "")
        if id not in cache:
            print(f"{whenstr} {id} DELETED")
            return
        print(f"{whenstr} {id} DELETED ({prettyObj(cache[id])})")
        del cache[id]
        return
    if id in cache:
        #diff = YouchamaJsonDiffer(cache[id], obj).get_diff()
        diff = DeepDiff(cache[id], obj)
        print(f"{whenstr} {id} DIFF ({prettyObj(cache[id])})")
        write(f"{whenstr}-@{id}-DIFF", diff.to_json())
        write(f"{whenstr}-@{id}-UPDATED", obj)
    else:
        print(f"{whenstr} {id} NEW ({prettyObj(obj)})")
        write(f"{whenstr}-@{id}-NEW", obj)
    cache[id] = obj

# Iterate over the output line by line
buf: list[str] = []
if process.stdout:
    for line in process.stdout:
        when = datetime.now()
        buf.append(line)
        if line != "}\n" and line != "]\n":
            #print(f"LINE:({line})")
            continue
        # Parse the JSON object from each line
        try:
            data = json.loads("".join(buf))
            buf = []
        except json.JSONDecodeError:
            print(f"Error decoding JSON")
            buf = []
            continue
        if isinstance(data, list):
            print("Have an array")
            for obj in data:
                handleObject(when, obj)
        else:
            print("Have non-array")
            handleObject(when, data)
        # Handle the JSON object as needed
        #print("Received JSON object:", data)
        # Add your handling logic here
