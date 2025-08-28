# Import libs
import hashlib
import os
from time import sleep, strftime
from getpass import getuser

#calculate file hash
def calc_file_hash(filepath):
    """calculates the SHA512 hash of a file"""
    hash_SHA512 = hashlib.sha512()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
        	hash_SHA512.update(chunk)
    return hash_SHA512.hexdigest()


#erase baseline if it exists
def erase_baseline():
    """erases the baseline file if it already exists"""
    if os.path.exists("baseline.txt"):
    	os.remove("baseline.txt")


#calculate new baseline
def calc_new_baseline():
    """Calculates the new baseline of file hashes, ignores certain file types.""" 
    erase_baseline()
    files_directory = './Files'
    if not os.path.exists(files_directory):
        os.makedirs(files_directory)
    files = [f for f in os.listdir(files_directory) if os.path.isfile(os.path.join(files_directory, f)) and not f.startswith('.')]
    with open('baseline.txt', 'w') as baseline_file:
        for f in files:
            file_path = os.path.join(files_directory, f)
            file_hash = calc_file_hash(file_path)
            baseline_file.write(f'{file_path} | {file_hash} \n')
            
# Track file changes over time
def log_event(event):
    with open("audit_log.txt", "a") as log:
        log.write(f"[{strftime('%Y-%m-%d %H:%M:%S')}] {event}\n")

#begin monitoring 
def begin_monitoring():
    """Monitor files for changes, deletions, and new copies based on the saved baseline, including detailed audit logs."""
    path_hash_dict = {}
    
    # Load the filepaths and hashes from baseline.txt
    with open('baseline.txt', 'r') as baseline_file:
        for line in baseline_file:
            path, file_hash = line.strip().split("|")
            path_hash_dict.update({path.strip() : file_hash.strip()})
    # Begin continuously monitoring the files with saved baseline'
    try:
        while True:
            sleep(5)
            files_directory = './Files'
            files = [os.path.join(files_directory, f) for f in os.listdir(files_directory) if os.path.isfile(os.path.join(files_directory, f))]
	
            # Check if a file has been deleted
            for baseline_file_path in path_hash_dict:
                if not os.path.exists(baseline_file_path):
                    print(f"File deleted: {baseline_file_path}")
                    log_event(f"File deleted: {baseline_file_path}")

            # Check if a file has been modified
            for file in files: 
                if file in path_hash_dict:
                    new_hash = calc_file_hash(file)
                    old_hash = path_hash_dict[file]
                    if new_hash != old_hash:
                        print(f"File has been modified! BEFORE: {old_hash}, AFTER: {new_hash}")
                        log_event(f"File has been modified! BEFORE: {old_hash}, AFTER: {new_hash}")
 
	        
            # Check if a file has been added
            for file in files:
                if file not in path_hash_dict:
                    print(f"New file detected: {file}")
                    log_event(f"New file detected: {file}")
    except Exception as e:
        print(f"Error occurred: {e}")
        
    

#main
def main():
    print("\nWhat would you like to do? \n")
    print("	A) Collect new baseline?")
    print("	B) Start monitoring files with saved baseline? \n")
    response= input("Please enter 'A' or 'B': ").upper()

    if response == 'A':
        calc_new_baseline()
        print("New baseline collected successfully.")
    elif response == 'B': 
        print("Monitoring started. Logging to audit_log.txt. Press Ctrl+C to stop.")
        begin_monitoring()

if __name__ == '__main__':
    main()
