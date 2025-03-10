import os
import glob
import re
import secrets
import string


def find_verilog_files(root_path):
    # List to store the paths of .v and .sv files
    verilog_files = []

    # Walk through the directory tree
    for root, dirs, files in os.walk(root_path):
        # Use glob to find .v and .sv files in the current directory
        verilog_files.extend(glob.glob(os.path.join(root, '*.v')))
        verilog_files.extend(glob.glob(os.path.join(root, '*.sv')))

    return verilog_files

def extract_verilog_ports(filename):
    with open(filename, 'r',errors="ignore") as f:
        content = f.read()
    content = re.sub(r'//.*', '', content)            
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)            
    pattern = r'\b(?:input|output|inout)\b\s*((?:[^;)]|$[^)]*$)*)'
    matches = re.findall(pattern, content, flags=re.IGNORECASE)
    ports = []
    for match in matches:
        ports.extend([v.strip() for v in match.split(',')])
    ports = [item.split()[-1] for item in ports]
    #print(ports)
    return ports

def extract_wires_regs(verilog_file):
    #print(f'input verilog file is {verilog_file}')
    with open(verilog_file, 'r',errors="ignore") as f:
        content = f.read()

    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r'//.*', '', content, flags=re.MULTILINE)
    content = re.sub(r'\s+', ' ', content)

    port_names = extract_verilog_ports(verilog_file)
    wire_reg_names = []
    wire_reg_pattern = re.compile(r'\b(wire|reg)\b\s*(?:$$.*?$$)?\s*([^;]+);', re.IGNORECASE)
    for match in wire_reg_pattern.finditer(content):
        vars_part = match.group(2).strip()
        if vars_part:
            vars_list = [var.strip() for var in vars_part.split(',')]
            wire_reg_names.extend(vars_list)
    wire_reg_names = [item.split()[-1] for item in wire_reg_names]
    result = [name for name in wire_reg_names if name not in port_names]
    #print(f"port names {port_names}")
    #print(f"var name {wire_reg_names}")
    #print(f"results {result}")
    return result

def replace_whole_word(text, old_word, new_word, case_sensitive=True):
    pattern = r'''
    (?<!\.)                               
    \b{0}\b                      
    (?!\()                            
    '''.format(re.escape(old_word))
    
    flags = re.VERBOSE | (0 if case_sensitive else re.IGNORECASE)
    return re.sub(pattern, new_word, text, flags=flags)

original_text = "catapult cat CAT Cat. cat123"
result = replace_whole_word(original_text, 'cat', 'dog', case_sensitive=False)

def generate_random_mapping(input_list):
    def _generate_random_str():
        first_char = secrets.choice(string.ascii_letters)
        remaining = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(31))
        return first_char + remaining
    return {item: _generate_random_str() for item in input_list}

def write_file_with_directories(file_path, content):
    # Extract the directory part of the file path
    directory = os.path.dirname(file_path)
    # Create the directory if it doesn't exist
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(file_path, 'w') as file:
        file.write(content)




print('''
==============================================================================
                RTL Encryption Script Start
Script Flow:
  1. get all .v .sv files @ Root Path
  2. loop i for all files:
     a.get all reg & wire names
     b.filter input/output/inout names
     c.generate rand str 32-len-str :start wit a-z/A-Z
     d.recording encryption seed var-str <==> rand-str
     e.replace var,rand
     f.gen new file & rand-str-file
==============================================================================
''')

root_path_str = str(os.environ.get('ROOT_PATH'))
out_path_str = str(os.environ.get('OUT_ROOT_PATH'))
decrypt_path_str = str(os.environ.get('DECRYPT_ROOT_PATH'))

origin_v_file_lst = find_verilog_files(root_path_str)

with open('skip_file_name.lst', 'r') as file:
    content = file.read()
    skip_file_lst = content.split()

#print (origin_v_file_lst)
#print (skip_file_lst)

for f in origin_v_file_lst:
    file_name = f.split('/')[-1]
    if file_name in skip_file_lst:
        print(f'>>The current progress is: {file_name}      : skip file')
    else:
        src_f_dir = f
        dest_f_dir = f.replace(root_path_str,out_path_str)
        decrypt_f_dir = f.replace(root_path_str,decrypt_path_str)
        var_lst=extract_wires_regs(f)
        if len(var_lst) == 0:
            print(f'>>The current progress is: {src_f_dir}      valid var is empty skip file')
        else:
            print(f'>>The current progress is: {src_f_dir}  --->  {dest_f_dir}')
            rand_mapping = generate_random_mapping(var_lst)
            encrypt_verilog_str=''
            decrypt_lktable=''
            with open (src_f_dir,'r',errors="ignore")as file:
                src_verilog_str = file.read()
            encrypt_verilog_str=src_verilog_str
            for k,v in rand_mapping.items():
                origin_var=k
                new_var= v
                #encrypt_verilog_str = encrypt_verilog_str.replace(origin_var,new_var)
                encrypt_verilog_str=replace_whole_word(encrypt_verilog_str, origin_var,new_var, case_sensitive=True)
                decrypt_lktable = decrypt_lktable+origin_var+'    '+new_var+'\n'
            write_file_with_directories(dest_f_dir,encrypt_verilog_str)
            write_file_with_directories(decrypt_f_dir,decrypt_lktable)

