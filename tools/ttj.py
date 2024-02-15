from toolutils import split_into_files
import os
from utils import Logger, loadYaml


class MphDecorator :
    def __init__(self, config_file):
        self._config_file = config_file
        self._logger = Logger('MphDecorator')
        slef._config = None
        
    def _validate(self):
        if ( self._config_file == None ):
            raise Exception("Config file {} is not set. Set environment variable GENAI_CONFIG_FILE")
        
    def _loadYaml(self):
        self._config = loadYaml(self._config_file)


## basedir="c:/Users/91998/ai/gemini/lws/src/main/java"
## split_into_files(basedir, '../out/04-lms-books-microservices_output.txt')

basedir=os.getenv('BASE_PROJECT_FOLDER')
print('basedir: ', basedir)
genai_output_file=os.getenv('GENAI_OUTPUT_FILE')
print('genai_output_file: ', genai_output_file)

split_into_files(basedir, genai_output_file )
print('completed.')