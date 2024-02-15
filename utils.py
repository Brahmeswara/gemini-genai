import dotenv as dotenv
import os
import jsonschema
import yaml 

dotenv.load_dotenv()
print('Loaded environment variables')
print('DEBUG: ', os.getenv('DEBUG'))
 
class Logger:
    def __init__(self, module_name):
        self._module_name = module_name
        self._debug = os.getenv('DEBUG')
        if self._debug:
            print(f'[{module_name}] Debugging enabled')
            self._debug = True
    
    def _log(self, message, isLogEnabled):
        if ( isLogEnabled ):
            print(f'[{self._module_name}] {message}')
        
    def debug(self, message):
        self._log(message, self._debug)
            
    def info(self, message):
        self._log(message, True) 
        
    def error(self, message):
        self._log(message, True) 
        
    def setLevel(self, level):
        self._debug = level
        
# Validate the yaml file
schema = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "properties": {
        "version": {"type": "string"},
        "kind": {"type": "string"},
        "metadata": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["name"],
        },
        "spec": {
            "type": "object",
            "properties": {
                "chain": {"type": "boolean"},
                "prompts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "ctx": {"type": "string"},
                        },
                        "required": ["text"],
                    },
                },
            },
            "required": ["prompts"],
        },
    },
    "required": ["version", "kind", "metadata", "spec"],
}

class schemaValidate:      
    def validate(self, data):
        #jsonschema.validate(data, schema)
        return True
        
        
class SaveContent :
    def __init__(self, ctx):
        self._ctx = ctx
        self._logger = Logger('SaveContent')
        
    def _validate (self):
        if ( self._ctx == None ):
            raise Exception("Context is not set")
        
        if ( self._ctx.get('output_to_dir') == None ):
            raise Exception("Output directory is not set")
        
    def readFromFile(self, file_name):
        self._validate()
        file_path = os.path.join(self._ctx.get('output_to_dir'), file_name)
        self._logger.debug(f'file_path: {file_path}')
        with open(file_path, 'r') as infile:
            content = infile.read()
            infile.close()
            self._logger.info(f'Content read from file: {file_path}')
            return content
        
    def _createDirectory(self):
        self._validate()
        output_to_dir = self._ctx.get('output_to_dir')
        self._logger.debug(f'output_to_dir: {output_to_dir}')
        if not os.path.exists(output_to_dir):
            os.makedirs(output_to_dir)
            self._logger.info(f'Directory created: {output_to_dir}')
            
    def save(self, content, file_name):
        self._validate()
        self._createDirectory()
        file_path = os.path.join(self._ctx.get('output_to_dir'), file_name)
        self._logger.debug(f'file_path: {file_path}')
        with open(file_path, 'w') as outfile:
            outfile.write(content)
            outfile.close()
            self._logger.info(f'Content saved to file: {file_path}')
        

def loadYaml (config_yaml_file):
    if ( os.path.isfile(config_yaml_file) == False ):
        raise Exception("Config file {} not found", config_yaml_file)
    
    print('Loading config file: {}'.format(config_yaml_file))
    
    temp_config = {}
    with open(config_yaml_file, 'r') as yaml_file:
        temp_config = yaml.safe_load(yaml_file)
        
    print('Done Loading config file: {}'.format(config_yaml_file))
    return temp_config

            
    