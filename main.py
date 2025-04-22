import os
import sys
import subprocess

def clear():
    # Clear the console screen
    os.system('cls' if os.name == 'nt' else 'clear')

def create_bins(original_list, num_bins):
    # Sort the original list based on the second element of each sublist in descending order
    sorted_list = sorted(original_list, key=lambda x: x[1], reverse=True)

    # Initialize a list to keep track of the sum of the second element in each bins
    bins_sums = [0] * num_bins

    # Initialize a list of empty bins
    bins = [[] for _ in range(num_bins)]

    # Iterate through the sorted list and assign each item to the bins with the smallest current sum
    for item in sorted_list:
        min_bins_index = min(range(num_bins), key=lambda i: bins_sums[i])
        bins[min_bins_index].append(item)
        bins_sums[min_bins_index] += item[1]

    return bins

def stats(dirs):
    total_size = 0
    min_size = 0
    max_size = 0

    for directory in dirs:
        try:
            # Loop through directories and get size of each
            dir_size = 0
            for root, _, files in os.walk(directory):
                for file in files:
                    dir_size += os.path.getsize(os.path.join(root, file))

            # Set variable values
            if total_size == 0:
                min_size = dir_size
                max_size = dir_size
            elif dir_size > max_size:
                max_size = dir_size
            elif dir_size < min_size:
                min_size = dir_size
            total_size += dir_size
        except:
            pass

    return round((total_size / len(dirs)) / (1024.0 ** 2), 2), round(min_size / (1024 ** 2), 2), round(max_size / (1024 ** 2), 2)

def delete_empty_dirs(orig_folder_path):
    # Delete all empty directories in orig_folder_path
    for folder_path, _, _ in os.walk(orig_folder_path, topdown=False):
        try:
            os.rmdir(folder_path)
        except:
            pass

def command_gen(new_path, UNCpath, file):
    if UNCpath:
        return rf'Move-Item -LiteralPath "\\?\UNC\{file[2][2:]}" -Destination "\\?\UNC\{new_path[2:]}"'
    elif len(new_path) >= 260:
        return rf'Move-Item -LiteralPath "\\?\{file[2]}" -Destination "\\?\{new_path}"'
    else:
        return rf'Move-Item -Path "{file[2]}" -Destination "{new_path}"'

def run_commands(cmds):
    # Run commands in powershell with specified chunk size to avoid errors
    chunk_size = 99
    for i in range(0, len(cmds), chunk_size):
        subprocess.run(["powershell", "-Command", '\n'.join(cmds[i:i + chunk_size])])

# Validate path from input
UNCpath = False
clear()
print('')
while True:
    orig_folder_path = input("\n    Enter path to folder:  ")
    # Remove surrounding quotations if present
    if orig_folder_path.endswith('"'):
                orig_folder_path = orig_folder_path[1:-1]
    try:
        # Validate path exists
        test = os.chdir(orig_folder_path)
        # Set UNCpath to true if path is UNC
        if orig_folder_path.startswith('\\\\'):
            UNCpath = True
    except:
        clear()
        print('\n\n    Invalid path.')
        continue
    break

# Search in subfolders?
yes_no = {1: True, 2: False}
clear()
print('')
while True:
    try:
        subfolder_choice_input = int(input('\n    Search in subfolders?  (1 = Yes, 2 = No)  '))
        subfolder_choice = yes_no[subfolder_choice_input]
    except:
        clear()
        print('\n\n    Invalid choice.')
        continue
    break

# Gather file information
file_list = []
non_ocr_list = []
if subfolder_choice: # Search within all subfolders
    for root, dirs, files in os.walk(orig_folder_path):
        for file in files:
            # If PDF, add to file_list, else add to non_ocr_list
            if file.endswith(".PDF") or file.endswith(".pdf"):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                file_list.append([file, file_size, file_path])
            else:
                non_ocr_list.append([file, '', os.path.join(root, file)])

else: # Only search within main folder    
    for file in os.listdir(orig_folder_path):
        # If PDF, add to file_list, else add to non_ocr_list
        if file.endswith(".PDF") or file.endswith(".pdf"):
            file_path = os.path.join(orig_folder_path, file)
            file_size = os.path.getsize(file_path)
            file_list.append([file, file_size, file_path])
        else:
            non_ocr_list.append([file, '', os.path.join(orig_folder_path, file)])

# Exit script if no files are found
if file_list == []:
    clear()
    input('\n\n    No files found.  Hit enter to exit ...')
    sys.exit()

# Validate no. of bins is valid
clear()
print('')
while True:
    try:
        num_bins = int(input('\n    Enter number of bins:  '))
        if num_bins <= 0:
            raise Exception
    except:
        clear()
        print('\n\n    Invalid input.')
        continue
    break

# Create bins given list of files and no. of bins
bins = create_bins(file_list, num_bins)

# Set variables for folder creation / file moving
folder_num = 1
fill_amount = len(str(num_bins)) + 1
files_to_move = len(file_list)
files_moved = 0

commands = []
dirs = []

# Create bins + Move-File commands
for bin in bins:
    # For each bin, ensure folder exists
    new_dir = os.path.join(orig_folder_path, str(folder_num).zfill(fill_amount))
    try:
        os.mkdir(new_dir)
    except:
        pass
    dirs.append(new_dir)

    # For each file, create Move-File command
    for file in bin:
        new_path = f'{orig_folder_path}\{str(folder_num).zfill(fill_amount)}\{file[0]}'
        if new_path != file[2]:
            commands.append(command_gen(new_path, UNCpath, file))

    folder_num += 1

# Run commands in chunks, delete all empty dirs in root folder
clear()
print('\n\n    PDF binning has started - Check folder for progress...')
run_commands(commands)
delete_empty_dirs(orig_folder_path)

# Move non OCR docs?
if non_ocr_list != []:
    clear()
    print('')
    while True:
        try:
            ocr_choice_input = int(input('\n    Move Non OCR documents?  (1 = Yes, 2 = No)  '))
            ocr_choice = yes_no[ocr_choice_input]
        except:
            clear()
            print('\n\n    Invalid choice.')
            continue
        break

    if ocr_choice:
        clear()
        print('\n\n    Moving Non OCR documents ...')
        non_ocr_list_commands = []
        # Create Move-File commands
        for file in non_ocr_list:
            new_path = f'{orig_folder_path}\\Non OCR\{file[0]}'
            if new_path != file[2]:
                non_ocr_list_commands.append(command_gen(new_path, UNCpath, file))

        try:
            os.mkdir(os.path.join(orig_folder_path, 'Non OCR'))
        except FileExistsError:
            pass
        except Exception as e:
            clear()
            input(f'\n\n    Error:  {e}.  Hit enter to exit ...')
            sys.exit()

        # Run commands in chunks, delete all empty dirs in root folder
        run_commands(non_ocr_list_commands)
        delete_empty_dirs(orig_folder_path)


# Finishing
clear()
avg_size, min_size, max_size = stats(dirs)
print(f'\n\n    {num_bins} bins created.\n\n    Avg. size {avg_size} MB\n    Min size {min_size} MB\n    Max size {max_size} MB')
input('\n    Hit enter to exit ...')