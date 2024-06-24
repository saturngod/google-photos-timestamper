import os
import json
import sys
from pathlib import Path
import re

stem_regex = r'.*\(\d+\)\..*'

def check_file_exists(file_path):
    return os.path.exists(file_path)


def get_alike_regex(filename):
    tokens = filename.split(".")
    name = re.escape(".".join(tokens[0:len(tokens) - 1]))
    ext = re.escape(tokens[len(tokens) - 1])
    return fr".*{name}( (\d{{1,2}}\.){{2}}\d{{1,2}} PM)+\.{ext}\..*"


def get_alike_regex_with_duplication(filename):
    return fr".*{re.escape(filename)}( (\d{{1,2}}\.){{2}}\d{{1,2}} PM)+\..*"


def move_duplication_string(path):
    pattern = r"(.*)\((.*?)\)(\..*)"
    match = re.search(pattern, path)
    if match:
        new_path = match.group(1) + match.group(3) + "(" + match.group(2) + ")"
        return new_path
    else:
        return path


def get_alike_json(path):
    dir_path = os.path.dirname(path)
    file_name = os.path.basename(path)
    jsons = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.endswith('.json')]
    regex = get_alike_regex(file_name)
    for json in jsons:
        if re.match(regex, json):
            return json

    # Try with duplication

    file_name = os.path.basename(move_duplication_string(path))
    regex = get_alike_regex_with_duplication(file_name)
    for json in jsons:
        if re.match(regex, json):
            return json

# def change_extension(image_path, new_extension):
#     return image_path.with_suffix(new_extension)

def change_extension(path,extension):   
    
    last_dot_index = path.rfind('.')
    if last_dot_index != -1:
        # Remove the existing extension
        path = path[:last_dot_index]
    # Append the new extension
    return f"{path}{extension}"

def final_change_last_remove_character(path):
    file = path[:-4]
    return f"{file}"

def try_update_json_path_with_extensions(image_path, extensions):
    for extension in extensions:
        new_path = change_extension(image_path, extension)
        potential_json_path = Path(new_path + ".json")
        # print(potential_json_path)
        if check_file_exists(potential_json_path):
            return potential_json_path
        else:
            potential_json_path = Path(move_duplication_string(new_path) + ".json")
            
            if check_file_exists(potential_json_path):
                return potential_json_path
            
    return None

def transform_string(s):
	regex = r"\((\d+)\)\.(\w{3})$"
	subst = r".\2(\1)"
	result = re.sub(regex, subst, s, 0, re.MULTILINE)
	return result

def editedPath(image_path):
    
    #if string contain '-edited', remove that part
    if "-edited" in image_path:
        #remove -edited from string
        new_path = image_path.replace("-edited", "")
        possible_json = Path(new_path + ".json")
        # print(possible_json)
        if check_file_exists(possible_json):
            return possible_json
        else:
            possible_json = Path(move_duplication_string(new_path) + ".json")
            # print(possible_json)
            if check_file_exists(possible_json):
                return possible_json
    return None
    
def get_json_remove_last_extension(image_path):
    file = image_path[:-5]
    return f"{file}"

def only46(image_path):
    directory, file_name = os.path.split(image_path)
    max_length = 46
    # Truncate the file name to the specified maximum length
    truncated_file_name = file_name[:max_length]

    # Reassemble the full path with the truncated file name
    truncated_file_path = os.path.join(directory, truncated_file_name)

    return truncated_file_path

def get_json_remove_last_extension_but_not_ext(image_path):
    # Regular expression pattern to match the part we need to remove the last character before
    pattern = r"(.*)(\d)(\((\d+)\))\.(\w{3})"

    
    # Regular expression pattern to match the part we need to remove the last character before
    pattern = r"(\d|\w)(\((\d+)\))\.(\w{3})"

    # Replace the last character before the pattern
    new_filename = re.sub(pattern, r'\2.json', image_path)
    
    return new_filename

def get_json_data(image_path):
    json_path = Path(image_path + ".json")
    if not check_file_exists(json_path):
        json_path = Path(move_duplication_string(image_path) + ".json")
        if not check_file_exists(json_path):
            extensions = [".HEIC", ".jpg", ".JPG", ".",".png", ".PNG",".mov",".MOV",".mp4",".MP4"]
            json_path = try_update_json_path_with_extensions(image_path, extensions)
            
            if json_path is None:
                
                json_path = editedPath(image_path)
                
                if json_path is None:
                    new_path = transform_string(image_path)
                    json_path = Path(move_duplication_string(new_path) + ".json")
                    if not check_file_exists(json_path):
                        new_path = final_change_last_remove_character(image_path)
                        json_path = Path(move_duplication_string(new_path) + ".json")
                        if not check_file_exists(json_path):
                            new_path = get_json_remove_last_extension(image_path)
                            json_path = Path(new_path + ".json")
                            if not check_file_exists(json_path):
                                new_path = get_json_remove_last_extension(image_path)
                                json_path = Path(move_duplication_string(new_path) + ".json")
                                if not check_file_exists(json_path):
                                    new_path = get_json_remove_last_extension_but_not_ext(image_path)
                                    if ".json" in new_path:
                                        json_path = Path(new_path)
                                        if not check_file_exists(json_path):
                                            print("NOT FOUND >>> " + str(image_path) + " | " + str(json_path))
                                            return
                                    else:
                                        
                                        json_path = Path(only46(image_path) + ".json")
                                        
                                        if not check_file_exists(json_path):
                                            print("NOT FOUND >>> " + str(image_path) + " | " + str(json_path))
                                            return
                                        
                                        
                            
    json_data = None
    try:
        with open(json_path, 'r') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        try:
            with open(Path(image_path + ".json"), 'r') as f:
                json_data = json.load(f)
        except FileNotFoundError:
            try:
                # Remove the "-edited" from the file name
                no_edited = image_path.replace("-edited", "")
                with open(Path(no_edited + ".json"), 'r') as f:
                    json_data = json.load(f)
            except FileNotFoundError:
                try:
                    with open(Path(get_alike_json(image_path)), 'r') as f:
                        json_data = json.load(f)
                except FileNotFoundError:
                    print(f"Could not find JSON file for {image_path}")
                    return
                # os.remove(image_path)
    return json_data


def update_image_metadata(image_path):
    
    # Get the timestamp from the JSON file
    json_data = get_json_data(image_path)

    timestamp = json_data['photoTakenTime']['timestamp']
    # Convert the timestamp from string to float
    timestamp = float(timestamp)
    # Update the image's creation time
    os.utime(image_path, (timestamp, timestamp))


path = sys.argv[1]

for dirpath, dirnames, filenames in os.walk(path):
    for filename in filenames:
        if not filename.endswith('.json') and filename != '.DS_Store':
            file_path = os.path.join(dirpath, filename)
            
            if(check_file_exists(file_path)): 
                update_image_metadata(file_path)
                # try:
                #     update_image_metadata(file_path)
                # except:
                #     print("Could not update image creation time for " + file_path)
