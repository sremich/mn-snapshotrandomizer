# mn-snapshotrandomizer
This is a script to create random routing snapshots in Riedel Communications MediorWorks software.

Options:

"-f", "--file" - Path to the CSV file containing frame data

"-n", "--num_snapshots" - Number of snapshots to generate (1-35, default: 10)

"-o", "--output" - Output file name (default: randomized_snapshots.json)




The import csv format is as follows:

ID,Type,Source Priority,Destination Priority,Exclude from Injest Priority Destinations

See "example.csv"
