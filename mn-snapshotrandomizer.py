"""
Randomized MediorNet Routing Snapshot Generator

Copyright (C) [Year] [Your Name]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import csv
import json
import random
import argparse

##CSV file import
def read_frame_data(csv_filename):
    frames = {
        'std': [], 'std_3g': [], 'std_3g_in': [], 'std_3g_out': [], 
        'mv': [], 'hz': [], 'ingest_priority': [], 
        'ingest_dest_exclude': [], 'priority': []
    }
    
    with open(csv_filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            frame_id = int(row['ID'])
            frame_type = row['Type']
            source_priority = row.get('Source Priority') == 'x'
            dest_priority = row.get('Destination Priority') == 'x'
            exclude_ingest_dest = row.get('Exclude from Injest Priority Destinations') == 'x'

            frames[frame_type].append(frame_id)  
            if source_priority:
                frames['ingest_priority'].append(frame_id)
            if dest_priority:
                frames['priority'].append(frame_id)
            if exclude_ingest_dest:
                frames['ingest_dest_exclude'].append(frame_id)
    return frames

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Randomized MediorNet Routing Snapshot Generator")
    parser.add_argument("-f", "--file", required=True, help="Path to the CSV file containing frame data")
    parser.add_argument("-n", "--num_snapshots", type=int, default=10, choices=range(1, 36), help="Number of snapshots to generate (1-35)")
    parser.add_argument("-o", "--output", default="randomized_snapshots.json", help="Output file name (default: randomized_snapshots.json)")

    args = parser.parse_args()

    frames = read_frame_data(args.file)

random_seed = random.randint(1, 9999999)
random.seed(random_seed)

# Frame and channel data
## frames_std_3g is a 24x24 unit, frames_std_3g_in is a 32x16 unit, and frames_std_3g_out is a 16x32 unit
frames_std = frames['std']
frames_std_3g = frames['std_3g']
frames_std_3g_in = frames['std_3g_in']
frames_std_3g_out = frames['std_3g_out']
frames_mv = frames['mv']
frames_hz = frames['hz']

#Priority Groups
frames_ingest_priority = frames['ingest_priority']
frames_ingest_dest_exclude = frames['ingest_dest_exclude']
frames_priority = frames['priority']

# Combine all frames and shuffle
frames_all = frames_std + frames_mv + frames_hz + frames_std_3g + frames_std_3g_in + frames_std_3g_out
random.shuffle(frames_all)

# Source and destination channel definitions
channels_std_source = [f"1.{x}" for x in [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34, 36, 37, 38, 39]]
channels_std_3g_source = [f"1.{x}" for x in [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 26, 27, 31, 32, 36, 37]]
channels_std_3g_out_source = [f"1.{x}" for x in [1, 2, 6, 7, 11, 12, 16, 17, 21, 22, 26, 27, 31, 32, 36, 37]]
channels_mv_source = [f"1.{x}" for x in [1, 2, 3, 4, 6, 7, 8, 9]] + [f"{x}.0" for x in range(6, 14)]
channels_hz_source = [f"1.{x}" for x in [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34, 36, 37, 38, 39]] + [f"{y}.{x}" for y in range(4, 20) for x in [10, 11, 12, 13]]

channels_std_dest = [f"2.{x}" for x in [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34, 36, 37, 38, 39]]
channels_std_3g_dest = [f"2.{x}" for x in [1, 2, 6, 7, 11, 12, 16, 17, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34, 36, 37, 38, 39]]
channels_std_3g_in_dest = [f"2.{x}" for x in [1, 2, 6, 7, 11, 12, 16, 17, 21, 22, 26, 27, 31, 32, 36, 37]]
channels_mv_dest = [f"2.{x}" for x in [1, 2, 3, 4, 6, 7, 8, 9]] + [f"6.{x}" for x in range(1, 37)]
channels_hz_dest = [f"2.{x}" for x in [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34, 36, 37, 38, 39]] + [f"{y}.{x}" for y in range(4, 20) for x in [25, 26, 27, 28]]


def get_source_channels(frame_id):
    if frame_id in frames_std or frame_id in frames_std_3g_in:
        return channels_std_source
    elif frame_id in frames_mv:
        return channels_mv_source
    elif frame_id in frames_std_3g:
        return channels_std_3g_source
    elif frame_id in frames_std_3g_out:
        return channels_std_3g_out_source
    else:
        return channels_hz_source

def get_dest_channels(frame_id):
    if frame_id in frames_std or frame_id in frames_std_3g_out:
        return channels_std_dest
    elif frame_id in frames_mv:
        return channels_mv_dest
    elif frame_id in frames_std_3g:
        return channels_std_3g_dest
    elif frame_id in frames_std_3g_in:
        return channels_std_3g_in_dest
    else:
        return channels_hz_dest
    
# Function to get valid destinations for a source
def get_valid_destinations(source_frame, used_destinations):
    valid_destinations = []
    for dest_frame in frames_all:
        if dest_frame != source_frame and dest_frame not in frames_ingest_dest_exclude:
            for c in get_dest_channels(dest_frame):
                if (dest_frame, c) not in used_destinations:  # Check destination usage
                    valid_destinations.append((dest_frame, c))
    return valid_destinations

def all_sources_used(unused_sources):
    return not unused_sources

# Build snapshot
snapshot = {
    "version": 1,
    "snapshots": []
}

for snapshot_id in range(1, args.num_snapshots + 1):

    used_destinations = set()

    unused_sources = [(frame, channel) for frame in frames_all for channel in get_source_channels(frame)]
    unused_sources_reset = [(frame, channel) for frame in frames_all for channel in get_source_channels(frame)]

    current_snapshot = {
        "id": snapshot_id,
        "name": f"Randomized Snapshot {snapshot_id}",
        "comment": "",
        "deleteBeforeApplying": True,
        "connections": []
    }

    snapshot["snapshots"].append(current_snapshot)

    # Route ingest priority sources
    for source_frame in frames_ingest_priority:
        source_channels = get_source_channels(source_frame)
        random.shuffle(source_channels)
        for source_channel in source_channels:
            valid_destinations = get_valid_destinations(source_frame, used_destinations)
            if not valid_destinations:
                print(f"Warning: No valid destinations left for source ({source_frame}, {source_channel}) in snapshot {snapshot_id}")
                break  # Skip this source channel if no valid destinations exist
            dest_frame, dest_channel = random.choice(valid_destinations)
            used_destinations.add((dest_frame, dest_channel))  # Mark destination as used
            unused_sources.remove((source_frame, source_channel))
            current_snapshot["connections"].append({
                "sourceFrameId": source_frame,
                "sourceChannel": source_channel,
                "destinationFrameId": dest_frame,
                "destinationChannel": dest_channel,
                "bidir": False,
                "hopCount": 2,
                "locked": False
            })

    # Prioritize destination group 
    for dest_frame in frames_priority: 
        dest_channels = get_dest_channels(dest_frame)
        random.shuffle(dest_channels)
        for dest_channel in dest_channels:
            if (dest_frame, dest_channel) in used_destinations:
                continue
            while True:
                source_frame = random.choice(frames_all)
                source_channels = get_source_channels(source_frame)
                if source_frame != dest_frame:
                    if all_sources_used(unused_sources):  # Reset used sources if all are used
                        unused_sources = unused_sources_reset
                    source_channel = random.choice(source_channels)
                    if (source_frame, source_channel) in unused_sources:  # Check if source is used
                        used_destinations.add((dest_frame, dest_channel))
                        unused_sources.remove((source_frame, source_channel))
                        
                        current_snapshot["connections"].append({  
                        "sourceFrameId": source_frame,
                        "sourceChannel": source_channel,
                        "destinationFrameId": dest_frame,
                        "destinationChannel": dest_channel,
                        "bidir": False,
                        "hopCount": 2,
                        "locked": False
                        })
                    else:
                        continue

                    break

    # Randomize the rest (same as before)
    for dest_frame in frames_all:
        dest_channels = get_dest_channels(dest_frame)
        random.shuffle(dest_channels)
        looptest = 0

        for dest_channel in dest_channels:
            if (dest_frame, dest_channel) in used_destinations:
                continue

            while True:
                if all_sources_used(unused_sources) or looptest == 10000:  # Reset used sources if all are used
                    unused_sources = unused_sources_reset
                    looptest = 0
                else:
                    looptest = looptest + 1

                source_frame = random.choice(frames_all)
                source_channels = get_source_channels(source_frame)

                if source_frame != dest_frame:
                    source_channel = random.choice(source_channels)

                    if (source_frame, source_channel) in unused_sources:  # Check if source is used
                        used_destinations.add((dest_frame, dest_channel))
                        unused_sources.remove((source_frame, source_channel))

                        current_snapshot["connections"].append({  
                            "sourceFrameId": source_frame,
                            "sourceChannel": source_channel,
                            "destinationFrameId": dest_frame,
                            "destinationChannel": dest_channel,
                            "bidir": False,
                            "hopCount": 2,
                            "locked": False
                        })
                    else:
                        continue

                    break

    print(f"Done with snapshot {snapshot_id}/{args.num_snapshots}")

# Output as JSON
with open(args.output, 'w') as outfile:
    json.dump(snapshot, outfile, indent=4)
