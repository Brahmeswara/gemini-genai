import os
import re

def isFile_exists(path):
    return os.path.isfile(filepath)

def form_directory_name(parts):
    cleaned_parts = [part.replace('//', '').strip() for part in parts]
    directory_name = '/'.join(cleaned_parts)
    return directory_name

def form_java_pkg_name(parts):
    cleaned_parts = [part.replace('//', '').strip() for part in parts]
    pkg_name = '.'.join(cleaned_parts)
    return pkg_name

def convert_pkg_name_to_directory_name(text):
    parts = text.split()
    if 'package' in parts:
        parts.remove('package')
    directory_name = '/'.join(parts).replace(';', '').replace('.', '/')
    
    return directory_name

def rename_file_if_exists(filepath, fileprefix):
    if os.path.isfile(filepath):
        directory, filename = os.path.split(filepath)
        new_filename = fileprefix + '-' + filename
        new_filepath = os.path.join(directory, new_filename)
        os.rename(filepath, new_filepath)

# Returns new file name prefixing filepath with fileprefix
# otherwise, return the same filepath 
def get_prefixed_filename_if_exists(filepath, fileprefix):
    if os.path.isfile(filepath):
        directory, filename = os.path.split(filepath)
        new_filename = fileprefix + filename
        new_filepath = os.path.join(directory, new_filename)
        return new_filepath
    
    return filepath


def find_class_name(lines, pattern):
    for line in lines:
        match = re.search(pattern, line)
        if match:
            return line.split(' ')[2]  # Return the word right after "public class"

def getPackageName (lines):
    for line in lines:
        match = re.search(r'package (.*);', line)
        if match:
            return match.group(1)  # Return the word right after "package"
        

def split_into_files(basedir, filename, split_str):
    print('Splitting file: {}'.format(filename))
    with open(filename, 'r') as file:
        content = file.read()

    ##orig##blocks = content.split('```java\n')[1:]  # Split the content into blocks
    blocks = content.split(split_str)[1:]  # Split the content into blocks. 
    logger.debug('  --> blocks: {}'.format(len(blocks)))
    for block in blocks:
        lines = block.split('\n')
        pkg_line = getPackageName(lines)
        if ( pkg_line == None ):
            print('Error: package not found: {}'.format(lines))
            continue
        
        package_folder=convert_pkg_name_to_directory_name(pkg_line)
        class_name = find_class_name(lines, r'public class (.*)')
        if ( class_name == None ):
            class_name = find_class_name(lines, r'public interface (.*)')
        
        if ( class_name == None ):
            loggr.info(' Error: class or interface not found: {}'.format(pkg_line))
        
        print('pkg_line: {}'.format(pkg_line))
        print('class_name: {}'.format(class_name))
        print('pkg_folder: {}'.format(package_folder))
        
        
        # Create the directory structure for the package if it doesn't exist
        outdir = basedir + '/' + package_folder
        print('outdir: {}'.format(outdir))
        os.makedirs(outdir, exist_ok=True)
        
        out_filename = f'{outdir}/{class_name}.java'
        if ( os.path.isfile(out_filename)):
            print('file {} already exists'.format(out_filename))
            out_filename = get_prefixed_filename_if_exists(out_filename, "genai-generated-")
            print(' -> Writing to new file name: {}'.format(out_filename))
        
        print(' -> creating file {}'.format(out_filename))
        # Write the block to a .java file named after the class
        with open(out_filename, 'w') as java_file:
            ##java_file.write(pkg_line)
            java_file.write('\n'.join(lines[0:]).rstrip().rstrip("```"))  # Write the code to the file, removing the trailing ```
            java_file.close()
            
def saveToFile(lines, out_file, end_separator):
    with open(out_file, 'w') as java_file:
        # Write the code to the file, removing the trailing end_separator string
        java_file.write('\n'.join(lines).rstrip().rstrip(end_separator))  
        java_file.close()
        
def split_into_code_blocks(text, begin_sep, end_sep):
    pattern = r'{}(.*?){}'.format(re.escape(begin_sep), re.escape(end_sep))
    ##print(' p formed: {}'.format(pattern))
    matches = re.findall(pattern, text, re.DOTALL)
    return [match.strip() for match in matches]
        
def split_into_files_02(basedir, genai_output_file, ctx):
    ##logger.info('Splitting file: {}'.format(genai_output_file,))
    with open(genai_output_file, 'r') as file:
        content = file.read()
   
    begin_separator = ctx.get('begin-separator')
    end_separator = ctx.get('end-separator')
    ##print('begin_separator: {}'.format(begin_separator))
    ##print('end_separator: {}'.format(end_separator))
         
    ##print('------------------------------')    
    matches = split_into_code_blocks(content, begin_separator, end_separator)
    ##print('matches len: {}'.format(len(matches)))
    ##if ( matches ):
    ##    print('matches[0]: {}'.format(matches[0]))
    ##print('------------------------------') 
    
    ##orig##blocks = content.split('```java\n')[1:]  # Split the content into blocks
    ##blocks = content.split(begin_separator)[1:]  # Split the content into blocks. 
    blocks = split_into_code_blocks(content, begin_separator, end_separator)
    ##logger.debug('  --> blocks: {}'.format(len(blocks)))
    for block in blocks:
        lines = block.split('\n')
        
        if ( ctx.get('move-type').lower() == 'direct' ):
            out_file = basedir + '/' + ctx.get('save-to')
            saveToFile(lines, out_file, "```")
            continue
        
        ## else if ( ctx.get('move-type').lower() == 'package' ) 
        
        
        pkg_line = getPackageName(lines)
        if ( pkg_line == None ):
            print('Error: package not found: {}'.format(lines))
            continue
        
        package_folder=convert_pkg_name_to_directory_name(pkg_line)
        class_name = find_class_name(lines, r'public class (.*)')
        if ( class_name == None ):
            class_name = find_class_name(lines, r'public interface (.*)')
        
        if ( class_name == None ):
            loggr.info(' Error: class or interface not found: {}'.format(pkg_line))
        
        print('pkg_line: {}'.format(pkg_line))
        print('class_name: {}'.format(class_name))
        print('pkg_folder: {}'.format(package_folder))
        
        
        # Create the directory structure for the package if it doesn't exist
        outdir = basedir + '/' + package_folder
        print('outdir: {}'.format(outdir))
        os.makedirs(outdir, exist_ok=True)
        
        out_filename = f'{outdir}/{class_name}.java'
        if ( os.path.isfile(out_filename)):
            print('file {} already exists'.format(out_filename))
            out_filename = get_prefixed_filename_if_exists(out_filename, "genai-generated-")
            print(' -> Writing to new file name: {}'.format(out_filename))
        
        print(' -> creating file {}'.format(out_filename))
        # Write the block to a .java file named after the class
        saveToFile(lines[0:], out_filename, "```")
        
        ##with open(out_filename, 'w') as java_file:
        ##    ##java_file.write(pkg_line)
        ##    java_file.write('\n'.join(lines[0:]).rstrip().rstrip("```"))  # Write the code to the file, removing the trailing ```
        ##    java_file.close()
        
        
#basedir="c:/Users/91998/ai/gemini/lws/src/main/java"
#split_into_files(basedir, '../out/04-lms-books-microservices_output.txt')

"""
def split_into_files_old(basedir, filename):
    with open(filename, 'r') as file:
        content = file.read()

    blocks = content.split('```java\n')[1:]  # Split the content into blocks
    for block in blocks:
        lines = block.split('\n')
        pkg_line = lines[0]
        pkg_folder=convert_pkg_name_to_directory_name(pkg_line)
        
        class_line = lines[0]  # The first line should contain the package 
        wl=len(class_line.split('.'))
        class_name = class_line.split('.')[-1]  # Extract the class name
        package_folder=form_directory_name(class_line.split('.')[0:wl-1])
        package_name=form_java_pkg_name(class_line.split('.')[0:wl-1])
        #package_name = class_line.split(' ')[1].replace('.', '/')  # Extract and format the package name
        print('class_name: {}'.format(class_name))
        print('package_folder: {}'.format(package_folder))
        print('package_name: {}'.format(package_name))
        
        # Create the directory structure for the package if it doesn't exist
        outdir = os.path.join(basedir, package_folder)
        os.makedirs(outdir, exist_ok=True)

        print('creating file {}'.format(f'{outdir}/{class_name}.java'))
        pkg_line = f'package {package_name};\n'
        # Write the block to a .java file named after the class
        with open(f'{outdir}/{class_name}.java', 'w') as java_file:
            ##java_file.write(pkg_line)
            java_file.write('\n'.join(lines[1:]).rstrip('```'))  # Write the code to the file, removing the trailing ```

"""

def list_java_files(directory):
    files_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".java"):
                files_list.append(os.path.join(root, file))
                
    return files_list

