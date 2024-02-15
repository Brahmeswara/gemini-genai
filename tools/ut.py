
from toolutils import list_java_files
#from google_ai_tool import gemini_ai_assistant
from utils import Logger, SaveContent, loadYaml

import sys
import os
import re
 
# adding Folder_2 to the system path
#sys.path.insert(0, 'C:/Users/91998/ai/gemini/ai-gen/core')
from google_ai_tool import gemini_ai_assistant


class UnitTests :
    def __init__(self, config_file):
        self._config_file = config_file
        self._logger = Logger('UnitTests')
        self._logger.setLevel(True)
        self._sc = None

    def _validate (self):
        if ( self._config_file == None ):
            raise Exception("Config file {} is not set")
        
        self._config = loadYaml(self._config_file)
        self._source_dir = self._config.get('base-project-dir')   
    
        if ( self._source_dir == None ):
            raise Exception("Invalid confiugration base-project-dir  directory {} is not set")
        
        self._output_dir = self._config.get('output-dir')
        self._file_selection_include = self._config.get('file-selection-include')
        self._sc = SaveContent({'output_to_dir': self._output_dir})
        
    def initGeimini(self):
        ctx = {}
        ctx['api_key'] = os.getenv('GENAI_API_KEY')
        self._gemini = gemini_ai_assistant(ctx)

    def getFileContent(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            file.close()
            return content
        
    def generate_unit_test(self, prompt):
        res=self._gemini.generateContent([prompt])
        return res

    def create_directory_if_not_exists(self,path):
        directory, filename = os.path.split(path)
        self._logger.info(f'Creating directory: {directory}')
        os.makedirs(directory, exist_ok=True)
        return filename
    
    def write_unit_test(self, test_content, file_path):
        self.create_directory_if_not_exists(file_path)
        with open(file_path, 'w') as file:
            file.write(test_content)
            file.close()
            
        
    def getPrompt(self, content):
        p = "You are expert Java, Spring REST API Developer and tester.\n"
        p = p + "Write JUnit test cases for the following java cass. \n"
        p = p + "Package name of the generated unit test file should be same as the given java calss.\n"
        p = p + "Include the package name as first line \n"
        p = p + "if the java class uses @Data or @Builder annotation of lombok use the lombok builder to create the object.\n"
        p = p + "Return complete java code. \n"
        
        ##p = "Generate unit test cases for the java file given. \n "
        ##p = p + "Include the package name as first line \n"
        ##p = p + "and package name should be same as that of original java file given "
        ##p = p + "in the context.\n "
        ##p = p + "include all the imports based required for the generated test files.\n"
        ##p = p + "if the Book class is used in testing, then create the book class with empty constructor and use the setters to set the values.\n"
        ##p = p + "Generate unit test cases for java bean testing only for the classes that are annotated with @Entity. Do not use persistent manager\n"
        #p = p + "Use the jakarta.persistence package for all the jpa annotations\n"
        p = p + '"""\n' + content + '"""' + '\n'
        return p 


    def find_match(self, lines, pattern, word_index):
        for line in lines:
            match = re.search(pattern, line)
            if match:
                print('  --> match: {}'.format(line))
                return line.split(' ')[word_index]  # Return the word right after "public class"
        return None
    
    def isInterface(self, file_contents):
        res = self.find_match(file_contents, r'public interface (.*)', 2)
        if ( res == None ):
            print('-----> not an interface')
            return False
        
        print('-----> this is interface: {}'.format(res))
        return True

    def get_unittest_file_fullname(self, filepath, new_filename):
        directory, filename = os.path.split(filepath)
        new_filepath = os.path.join(directory, new_filename)
        return new_filepath
    
    def massage_and_write(self, prompt, content, ut_file_path):
        blocks = content.split('```java\n')[1:]  # Split the content into blocks
        for block in blocks:
            lines = block.split('\n')
            pkg_line = lines[0]
            #package_folder=convert_pkg_name_to_directory_name(pkg_line)
            class_name = self.find_match(lines, r'public class (.*)', 2)
            if ( class_name == None ):
                class_name = self.find_match(lines, r'public interface (.*)', 2)
                if ( class_name != None ):
                    print(' ==> Ignoring Interface : class or interface not found: {}'.format(find_class_name))
                    continue 
            
            if ( class_name == None ):
                class_name = self.find_match(lines, r'class (.*)', 1)   
                
            if ( class_name == None ):
                raise Exception('Error: class or interface not found: {}'.format(lines))
            
            print('pkg_line: {}'.format(pkg_line))
            print('class_name: {}'.format(class_name))
            ##print('pkg_folder: {}'.format(package_folder))
            
            
            # Create the directory structure for the package if it doesn't exist
            ##outdir = basedir + '/' + package_folder
            ##print('outdir: {}'.format(outdir))
            ##os.makedirs(outdir, exist_ok=True)
            
            ##out_filename = f'{outdir}/{class_name}.java'
            ##if ( os.path.isfile(out_filename)):
            ##    print('file {} already exists'.format(out_filename))
            ##    out_filename = get_prefixed_filename_if_exists(out_filename, "genai-generated-")
            ##    print(' -> Writing to new file name: {}'.format(out_filename))
            
            final_ut_filename  = self.get_unittest_file_fullname(ut_file_path, class_name + '.java');
            self.create_directory_if_not_exists(final_ut_filename)
            print(' -> creating file {}'.format(final_ut_filename))
            # Write the block to a .java file named after the class
            with open(final_ut_filename, 'w') as ut_file:
                ##java_file.write(pkg_line)
                ut_file.write('\n'.join(lines[0:]).rstrip().rstrip("```"))  # Write the code to the file, removing the trailing ```
                ut_file.close()
            
    def savePromptResponse(self, p, res, filepath):
        directory, filename = os.path.split(filepath)
        self._sc.save(p, filename + '_prompt.txt')
        self._sc.save(res, filename + '_output.txt')
        
    def generate_all(self): 
        self._validate()
        self.initGeimini()
        file_list = list_java_files(self._source_dir)
        file_count = 0
        for file_path in file_list:
            self._logger.info(f'\nGenerating Unit Tests for file: {file_path}')
            file_content = None
            file_content = self.getFileContent(file_path)
            if ( self.isInterface(file_content) ):
                print(' ==> Ignoring Interface: {}'.format(file_path))
                continue
            
            file_count += 1
            p = None
            ut = None
            p=self.getPrompt(file_content)
            ut=self.generate_unit_test(p)
            self.savePromptResponse(p, ut, file_path)
            write_path = file_path.replace('src/main', 'src/test')
            if ( file_path == write_path ):
                raise Exception(f'File path {file_path} is same as write path {write_path}')
            
            self._logger.info(f'Writing file: {write_path}')
            self.massage_and_write(p, ut, write_path)
            file_count += 1
        self._logger.info(f'Generated : {file_count} unit test cases')
        
        
if __name__ == "__main__":
    config_yaml=os.getenv('UT_CONFIGFILE')
    ut = UnitTests(config_yaml)
    ut.generate_all()