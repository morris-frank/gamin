#%%
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from math import radians
from sklearn.metrics.pairwise import haversine_distances
import datetime

def parse_tcx(file_path: str, start_slice: datetime.timedelta, endend_slice: datetime.timedelta):
    """
    cuts out one time slice from a tcx file
    """
    # Parse the XML file
    total_old_points = 0
    total_new_points = 0
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Namespace definition
    namespace = {'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}

    # Extract some basic information
    activities = root.find('tcx:Activities', namespace)
    for activity in activities.findall('tcx:Activity', namespace):
        # start_time = activity.find('tcx:Id', namespace).text
        start_time = datetime.datetime.strptime(activity.find('tcx:Id', namespace).text, "%Y-%m-%dT%H:%M:%S.%fZ")
        
        for lap in activity.findall('tcx:Lap', namespace):
            for track in lap.findall('tcx:Track', namespace):
                trackpooints_to_keep = []
                for trackpoint in track.findall('tcx:Trackpoint', namespace):
                    total_old_points += 1
                    point_time = datetime.datetime.strptime(trackpoint.find('tcx:Time', namespace).text, "%Y-%m-%dT%H:%M:%S.%fZ")
                    timedelta = point_time - start_time
                    if timedelta <= start_slice or timedelta >= endend_slice:
                        trackpooints_to_keep.append(trackpoint)
                        total_new_points += 1
                track.clear()
                track.extend(trackpooints_to_keep)
    #save the modified xml
    tree.write(Path(file_path).with_suffix('.mod.tcx'))

    # open file as string
    with open(Path(file_path).with_suffix('.mod.tcx'), 'r') as file:
        data = file.read()
        #delete first line
        data = data[data.find('\n')+1:]
        #add at the beginning the xml version
        header = """<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase
  xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
  xmlns:ns5="http://www.garmin.com/xmlschemas/ActivityGoals/v1"
  xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2"
  xmlns:ns2="http://www.garmin.com/xmlschemas/UserProfile/v2"
  xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns4="http://www.garmin.com/xmlschemas/ProfileExtension/v1">"""
        data = header + data
        data = data.replace("<ns2:TPX", "<ns3:TPX")
        data = data.replace("</ns2:TPX", "</ns3:TPX")
        data = data.replace("<ns2:Speed", "<ns3:Speed")
        data = data.replace("</ns2:Speed", "</ns3:Speed")   
        data = data.replace("<ns0:", "<")
        data = data.replace("</ns0:", "</")

    # write the modified xml
    with open(Path(file_path).with_suffix('.mod.tcx'), 'w') as file:
        file.write(data)
    
    print(f"Total old points: {total_old_points}")
    print(f"Total new points: {total_new_points}")


# parse_tcx("/Users/mfr/Downloads/activity_16735357433.tcx")
parse_tcx("/Users/mfr/Downloads/activity_16735363320.tcx", datetime.timedelta(hours=3,minutes=45,seconds=31), datetime.timedelta(hours=4,minutes=15,seconds=46))
# parse_tcx("/Users/mfr/Downloads/activity_16735359011.tcx")

# %%
