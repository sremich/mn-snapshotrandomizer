import json
import random

#Stevie made this hehe

# Frame and channel data
frames_std = [13, 14, 15, 16, 19, 20, 25, 26, 31, 32, 37, 38, 39, 40, 41, 42, 43, 44, 45, 49] # 21, 22, 27, 28, 33, 34, 46 has been removed
frames_mv = [1, 2, 3, 4, 5, 6, 17, 18, 23, 24, 29, 30, 35, 36, 47]
frames_hz = [7, 8, 10, 11, 12] # 9 has been removed

# Combine all frames and shuffle
frames = frames_std + frames_mv + frames_hz
random.shuffle(frames)

# Define priority groups
frames_ingest_priority = [7, 8, 10, 11, 12]
frames_ingest_dest_exclude = [44, 45, 47]
frames_priority = [44, 45, 47]

# Separate source and destination channels
## Commented out variables are the difference between 3G routing and 12G routing each 3G 2SI element

channels_std_source = [f"1.{x}" for x in [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34, 36, 37, 38, 39]]
#channels_std_source = [f"1.{x}" for x in [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 26, 27, 31, 32, 36, 37]]
channels_mv_source = [f"1.{x}" for x in [1, 2, 3, 4, 6, 7, 8, 9]] + [f"{x}.0" for x in range(6, 14)]
channels_hz_source = [f"1.{x}" for x in [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34, 36, 37, 38, 39]] + [f"{y}.{x}" for y in range(4, 20) for x in [10, 11, 12, 13]]

channels_std_dest = [f"2.{x}" for x in [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34, 36, 37, 38, 39]]
#channels_std_dest = [f"2.{x}" for x in [1, 2, 6, 7, 11, 12, 16, 17, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34, 36, 37, 38, 39]]
channels_mv_dest = [f"2.{x}" for x in [1, 2, 3, 4, 6, 7, 8, 9]] + [f"6.{x}" for x in range(1, 37)]
channels_hz_dest = [f"2.{x}" for x in [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34, 36, 37, 38, 39]] + [f"{y}.{x}" for y in range(4, 20) for x in [25, 26, 27, 28]]


def get_source_channels(frame_id):
    if frame_id in frames_std:
        return channels_std_source
    elif frame_id in frames_mv:
        return channels_mv_source
    else:
        return channels_hz_source

def get_dest_channels(frame_id):
    if frame_id in frames_std:
        return channels_std_dest
    elif frame_id in frames_mv:
        return channels_mv_dest
    else:
        return channels_hz_dest

# Build snapshot
snapshot = {
    "version": 1,
    "snapshots": []
}

for snapshot_id in range(1, 10):
    used_connections = set()  # Track used source-destination combinations
    used_destinations = set()
    used_sources = set()
    remaining_frames = [f for f in frames if f not in frames_priority]

    current_snapshot = {
        "id": snapshot_id,
        "name": f"Randomized Snapshot {snapshot_id}",
        "comment": "",
        "deleteBeforeApplying": True,
        "connections": []
    }
    snapshot["snapshots"].append(current_snapshot)

    # Function to get valid destinations for a source
    def get_valid_destinations(source_frame, used_destinations):
        valid_destinations = []
        for dest_frame in frames:
            if dest_frame != source_frame and dest_frame not in frames_ingest_dest_exclude:
                for c in get_dest_channels(dest_frame):
                    if (dest_frame, c) not in used_destinations:  # Check destination usage
                        valid_destinations.append((dest_frame, c))
        return valid_destinations
    
    # Function to check if all sources are used
    def all_sources_used(used_sources):
        for frame in frames:
            for channel in get_source_channels(frame):
                if (frame, channel) not in used_sources:
                    return False  # Found an unused source
        return True  # All sources are used

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
            used_connections.add((source_frame, source_channel, dest_frame, dest_channel))
            used_destinations.add((dest_frame, dest_channel))  # Mark destination as used
            used_sources.add((source_frame, source_channel))
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
                source_frame = random.choice(frames)
                source_channels = get_source_channels(source_frame)
                if source_frame != dest_frame:
                    if all_sources_used(used_sources):  # Reset used sources if all are used
                        used_sources.clear()
                    source_channel = random.choice(source_channels)
                    if (source_frame, source_channel) not in used_sources:  # Check if source is used
                        used_connections.add((source_frame, source_channel, dest_frame, dest_channel))
                        used_sources.add((source_frame, source_channel))
                        used_destinations.add((dest_frame, dest_channel))
                        
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
    for dest_frame in frames:
        dest_channels = get_dest_channels(dest_frame)
        random.shuffle(dest_channels)
        for dest_channel in dest_channels:
            if (dest_frame, dest_channel) in used_destinations:
                continue
            while True:
                source_frame = random.choice(frames)
                source_channels = get_source_channels(source_frame)
                if source_frame != dest_frame:
                    if all_sources_used(used_sources):  # Reset used sources if all are used
                        used_sources.clear()
                    source_channel = random.choice(source_channels)
                    if (source_frame, source_channel) not in used_sources:  # Check if source is used
                        used_connections.add((source_frame, source_channel, dest_frame, dest_channel))
                        used_sources.add((source_frame, source_channel))
                        used_destinations.add((dest_frame, dest_channel))

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

# Output as JSON
print(json.dumps(snapshot, indent=4))