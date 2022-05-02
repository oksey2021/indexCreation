#import yaml
import os
import re
import math
import configparser
from datetime import date
from collections import OrderedDict

PATH_TO_GLOBAL_INDEXES_CONF="master-apps/all_indexes_spl/local/indexes.conf"
PATH_TO_INDEXES_CONF="master-apps/all_indexes_user/local/indexes.conf"
PATH_TO_INDEXES_README="INDEXES_README.md"
PATH_TO_YAML_DIR="index_yaml"
REGEX_INDEX_NAME='^[a-z][a-z0-9\-_]+$'
REGEX_DATATYPE='^(event|metric)$'
PROTECTED_INDEX_NAMES=["main","catchall","monitor_summary","history","summary","volume"]

class IndexTrackerDuplicateIndex(Exception):
  def __init__(self,idx):
    self.idx = idx
    self.message = "Index {0} has already been defined.".format(idx["name"])
    super().__init__(self.message)

class IndexTracker:
  def __init__(self):
    self.byIndex = {}

  def addIndex(self,idx):
    # See if index already added
    if (idx["name"] in self.byIndex):
      raise IndexTrackerDuplicateIndex(idx)

    self.byIndex[idx["name"]] = idx

  def listByIndexes(self):
    return OrderedDict(sorted(self.byIndex.items()))

# Setup structure to track indexes across all YAML files.
iTrack = IndexTracker()

# Setup indexes.conf output file
f = open(PATH_TO_INDEXES_CONF, "w")
f.write("######################################################################################\n")
f.write("# IMPORTANT - DO NOT edit this file directly. This file is auto generated by the\n")
f.write("#             {0} Actions script. To add/edit an index, edit the YAML\n".format(os.path.basename(__file__)))
f.write("#             files in the '{0}' directory of the repository.\n".format(PATH_TO_YAML_DIR))
f.write("######################################################################################\n")

# Walk the files in the yaml directory.
for root, dirs, files in os.walk(PATH_TO_YAML_DIR):
    
    # For each file in the directory...
    for index_yaml in sorted(files):
        index_yaml_file = "{0}/{1}".format(root,index_yaml)
        
        # If the file ends in '.yaml'
        if (index_yaml_file.lower().endswith(".yaml")):
            print("Processing YAML file {0}".format(index_yaml_file))

            # Read the YAML file
            with open(index_yaml_file) as file:
                documents = yaml.full_load(file)


            # For each index...
            for idx in documents["indexes"]:
                print("  - Processing index {0}...".format(idx["name"]))

                # Verify that a description is provided and add to the index header
                if "description" not in idx:
                    raise Exception("A description is required for index {0} in file {1}.".format(idx["name"],index_yaml_file))
                f.write("# Description: {0}\n".format(idx["description"]))

                # Verify that owner is provided
                if "owner" not in idx:
                    raise Exception("Owner needs to be defined for index {0} in file {1}.".format(idx["name"],index_yaml_file))
                f.write("# Owner: {0}\n".format(idx["owner"]))
                
                # Validate index name syntax
                if not (re.match(REGEX_INDEX_NAME, idx["name"])):
                    raise Exception("Index name ({0}) must match regex of {1}".format(idx["name"],REGEX_INDEX_NAME))
                if idx["name"] in PROTECTED_INDEX_NAMES:
                    raise Exception("Index name ({0}) is a protected index name and can not be used.".format(idx["name"]))

                # Validate datatype value if provided
                if "datatype" in idx:
                  if not (re.match(REGEX_DATATYPE, idx["datatype"])):
                    raise Exception("Datatype value ({0}) is invalid. It must match the regex of {1}".format(idx["datatype"], REGEX_DATATYPE))
                    
                f.write("[{0}]\n".format(idx["name"]))
                f.write("homePath   = volume:hot/{0}/db\n".format(idx["name"]))
                f.write("coldPath   = volume:cold/{0}/colddb\n".format(idx["name"]))
                f.write("thawedPath = $SPLUNK_DB/{0}/thaweddb\n".format(idx["name"]))
                f.write("remote   = volume:s3/{0}\n".format(idx["name"]))

                # If datatype is provided, at it to the config.
                if "datatype" in idx:
                    f.write("datatype   = {0}\n".format(idx["datatype"]))
  
                # If retention_days is provided, convert to seconds and add as frozenTimePeriodInSecs 
                if "retention_days" in idx:
                    f.write("frozenTimePeriodInSecs = {0}\n".format(idx["retention_days"]*86400))

                f.write("\n")

                # Add index to global tracking array
                iTrack.addIndex(idx)

        # File does not end with .yaml
        else:
            print("Skipping non-YAML file {0}".format(index_yaml_file))
            
# Close the indexes.conffile            
f.close()

# Retrieve repo default frozenTimePeriodInSecs
config = configparser.ConfigParser()
config.read(PATH_TO_GLOBAL_INDEXES_CONF)
defaultFrozenDays=""
try:
    defaultFrozenDays=math.floor(int(config["default"]["frozenTimePeriodInSecs"])/86400)
except:
    defaultFrozenDays="(Default)"
    print("Could not determine default frozenTimePeriodInSecs from {1}. Using '{0}' in documentation.".format(defaultFrozenDays,PATH_TO_GLOBAL_INDEXES_CONF))

# Setup readme for documentation
print("Generating index readme file...")
d = open(PATH_TO_INDEXES_README,"w")
d.write("# Index Definitions\n\nThis document provides a summary of all the indexes defined in Splunk.\n\n")
d.write("|Index|Owner|Description|Retention (Days)|\n")
d.write("|-|-|-|-|\n")

listOfIndexes = iTrack.listByIndexes()
for i in listOfIndexes:
    idx = listOfIndexes[i]

    # Determine the retention days of the index
    retentionstr=""
    try:
        retentionstr = idx["retention_days"]
    except:
        retentionstr = "{0}<sup>*</sup>".format(defaultFrozenDays)

    # Write the table entry to the document
    d.write("|{0}|{1}|{2}|{3}|\n".format(idx["name"],idx["owner"],idx["description"],retentionstr))

d.write("\n_<sup>*</sup> - These indexes do not have a specified retention time and are using the system wide setting of {0} retention days._\n".format(defaultFrozenDays))
d.write("\n*This file is auto generated by the {0} Actions script. To edit any index information, please update the YAML file in the '{1}' directory of the repository through a pull request.*\n".format(os.path.basename(__file__),PATH_TO_YAML_DIR))
d.close()
