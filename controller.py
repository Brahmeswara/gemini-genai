import yaml 
import os 
import os.path
from utils import Logger, schemaValidate, SaveContent
import sys
##sys.path.insert(0, './core')
from google_ai_tool import gemini_ai_assistant
from toolutils import split_into_files_02

logger = Logger('controller')

class Controller ():
    
    def __init__(self, config_file):
        self._config_file = config_file
        self._yamls = {}
        self._prompts = {}
        self._responses = {}
        self._ctxs = {}
        self._config = None
        self._decorators = {}
        
    def _loadYaml (self, config_yaml_file):
        if ( os.path.isfile(config_yaml_file) == False ):
            raise Exception("Config file {} not found", config_yaml_file)
        
        logger.info('Loading config file: {}'.format(config_yaml_file))
        
        temp_config = {}
        with open(config_yaml_file, 'r') as yaml_file:
            temp_config = yaml.safe_load(yaml_file)
            
        logger.info('Done Loading config file: {}'.format(config_yaml_file))
        return temp_config

        
    def validateConfig(self):
        if ( self._config_file == None ):
            raise Exception("Main Configuration files are not set...\n set variable CONFIG_FILE to config file path")
        
        self._api_key = os.getenv('GENAI_API_KEY')
        if ( self._api_key == None ):
            raise Exception("GenAI API Key is not set. Please set variable GENAI_API_KEY")
        
        self._config = self._loadYaml(self._config_file)
        logger.debug('loaded config {}'.format(self._printConfig()))
        
    def loadExistingOutput(self, templateName, saveObj):
        # get template data
        logger.info('Loading existing output for template: {}'.format(templateName))
        template = self._yamls.get(templateName)
        isFlagSet = template.get('metadata').get('do-not-generate-take-existing-instead')
        logger.info('{} do-not-generate-take-existing-instead is set to {}'.format(templateName, isFlagSet))
        if ( isFlagSet == None or isFlagSet == False  ):
            return False 
        
        logger.info('{} do-not-generate-take-existing-instead is set to true. Do not generate'.format(templateName))
        ## read the prompt and output files
        templateOutputFile = templateName + '_output.txt'
        res = saveObj.readFromFile(templateOutputFile)
        self._responses[templateName] = res
        return True

        
    def generate(self):
        ctx = {'api_key' : self._api_key}
        sc = SaveContent(self._config)

        for yamlName, prompt in self._prompts.items():
            print('item: {}'.format(yamlName))
            prompts = prompt
                    
            ## load from the existing file, if template has flag set in metadata
            if ( self.loadExistingOutput(yamlName, sc) == True ):
                logger.info('Skipping generation for: {}. Data is loded from existing output file'.format(yamlName))
                continue
        
            gemini = gemini_ai_assistant(ctx)
            if ( self._ctxs.get(yamlName) != None ):
                tempCtx = self._getPromptContext(yamlName, self._ctxs.get(yamlName))
                logger.debug('generated: tempCtx: {}'.format(tempCtx))
                prompts = prompt + tempCtx
                logger.debug('generate: value: {}'.format(prompts))
                
            res : any ; 
            results : any
            try:
                res = gemini.generateContent([prompts])                    
                self._responses[yamlName] = res
                results = res
            except ValueError as verror:
                logger.error('error-1: {}'.format(verror))
                raise Exception(verror)
                
            except Exception as error:
                logger.error('error-2: {}'.format(error))
                raise Exception(error)
                
            logger.debug('response: {}'.format(self._responses.get(yamlName)))
            
            sc.save(prompts, yamlName + '_prompt.txt')
            sc.save(results, yamlName + '_output.txt')
            
    def process(self):
        for template_file in self._config.get('config_files'):
            logger.debug('Proessing template file: {}'.format(template_file))
            self._loadTemplateYAML(template_file)
            
    def _loadTemplateYAML(self, template_file):
        if ( os.path.isfile(template_file) == False ):
            raise Exception("Template file {} not found", template_file)
        
        tempConfig = self._loadYaml(template_file)
        self._validateGenAIConfigYAML(template_file, tempConfig)
        
        templateName = tempConfig.get('metadata').get('name')
        logger.debug('YAML Name (metadata.name): {}'.format(templateName))
        prompts = tempConfig.get('spec').get('prompts')
        ##logger.info('\t prompts 0: {}'.format(prompts[0].get('text')))

        self._yamls[templateName] = tempConfig
        self._prompts[templateName] = self._getPrompt(templateName, tempConfig)
        logger.debug('prompts 1: {}'.format(self._prompts[templateName]))
        self._decorators[templateName] = tempConfig.get('metadata').get('decorators')
        
      
    def _getPrompt(self, yamlName, config):
        prompt = config.get('spec').get('prompts')[0].get('text')
        logger.debug('\t Prompt is : {}'.format(prompt))
        ctx = config.get('spec').get('prompts')[0].get('ctx')
        ##ctx = self._getPromptContext(yamlName, config)
        logger.debug('\t Prompt ctx is : {}'.format(ctx))
        self._ctxs[yamlName] = ctx
        #if ( ctx != None ):
        #    prompt = prompt + ctx 
        #    
        return prompt
    
    def _getFormattedContextt(self, yamlName, contextText):
        template = self._yamls.get(yamlName)
        kind = template.get('kind')
        logger.info('\t kind is : {}'.format(kind))
        value = contextText 
        if ( kind.strip() == 'schmea-ddl' ):
            logger.info('\t     kind is : {}'.format(kind))
            value=contextText.replace('```sql', '"""').replace('```', '"""')
            
        if ( kind.strip() == 'schmea-to-openapi-spec' ):
            logger.info('\t     kind is : {}'.format(kind))
            value=contextText.replace('```yaml', '"""').replace('```', '"""')

        logger.debug('\t     formatted context is : {}'.format(value))
        return value
    
    def _getPromptContext(self, yamlName, ctx):
        #ctx = config.get('spec').get('prompts')[0].get('ctx')
        #logger.debug('001- Prompt ctx is : {}'.format(ctx))
        
        #ctx is an array of values 
        ctxs = self._ctxs.get(yamlName)
        logger.info('001- Prompt ctxs is : {}'.format(ctxs))
        if ( ctxs == None ):
            return None
        
        tempCtx = ''
        for ctx in ctxs:
            # see if value is specified
            value = ctx.get('value')
            logger.debug('\t 002- Prompt ctx value is : {}'.format(value))
            if ( value  ):
                logger.info(' taking the context from: value')
                tempCtx = tempCtx + value 
                continue
                
            # see if output-of is specified
            key = ctx.get('output-of')
            logger.info('\t 003- Prompt ctx key is : {}'.format(key))
            if ( key != None ):
                if ( self._responses.get(key) == None ):
                    raise Exception("Referenced yaml metadata.name is not valid: {}".format(key))
                    
                logger.info(' taking the contex from output-of {}'.format(key))
                value=self._getFormattedContextt(key, self._responses.get(key))
                tempCtx = tempCtx + value + "\n"
                
        logger.debug('\t 004- Prompt ctx temp is : {}'.format(tempCtx))
        return tempCtx     
        
        # else , it is an escaped error from config file validation
        #raise Exception("Prompt context is not set or YAML file is not valid")
        

    def _validateGenAIConfigYAML(self, yaml_file, config):
        logger.debug('Validating template file: {}'.format(config))
        sv = schemaValidate()
        sv.validate(config)
        
        logger.info('\t TO DO: All validations are not implemented yet')

                
    def _printConfig(self):
        print("pring config:\n", self._config)
        logger.info("output-to-dir: {}".format(self._config.get('output_to_dir')))
        logger.info('configfiles: {}'.format(self._config.get('config_files')))
        
    def _parseSaveProfile(self, save_profile):
        if ( save_profile == None ):
            return {}
        
        sp = {}
        for value in save_profile:
            logger.debug('_parseSaveProfile: value: {}'.format(value))
            sp[value.get('type')] = value 
            
        return sp
    
    ## for decorator
    def _getOutputPath(self, base_dir, target_type, config_data):
        if ( target_type == None ):
            return base_dir
        
        temp = config_data.get(target_type)
        if ( temp == None ):
            return base_dir
        
        if ( temp.get('prefix-path') == None ):
            return base_dir
        
        return base_dir + "/" + temp.get('prefix-path')
        

    
    def decorate(self):
        ##ctx = {'api_key' : self._api_key}
        ##sc = SaveContent(self._config)
        
        base_output_dir = self._config.get('output_to_dir')
        target_profile = self._config.get('target-project-profile')
        save_profile = self._parseSaveProfile(target_profile.get('save-config'))
        logger.info('decorate: save profile is: {}'.format(save_profile))
        decorator_base_dir = target_profile.get('base-dir') 
        group_id = target_profile.get('group-id')
        artifact_id = target_profile.get('artifact-id')
        
        genai_output_dir = self._config.get('output_to_dir')
        
        for templateName, target_decoration in self._decorators.items():
            if ( target_decoration == None ):
                logger.info('decorate: No decoration for template {}'.format(templateName))
                continue
            
            logger.info('Teamplate {} decoration: {}'.format(templateName, target_decoration))
            template_genai_output = genai_output_dir + '/' + templateName + '_output.txt'
            logger.info('\t template_genai_output: {}'.format(template_genai_output))
            logger.info('\t base_dir: {}'.format(decorator_base_dir))
            output_path = self._getOutputPath(decorator_base_dir, target_decoration.get('type'), save_profile)
            logger.info('\t output_path: {}'.format(output_path))
            
            ## form the context
            ctx = {}
            ctx['type'] = target_decoration.get('type')
            ctx['begin-separator'] = target_decoration.get('begin-separator')
            ctx['end-separator'] = target_decoration.get('end-separator')
            ctx['move-type'] = target_decoration.get('move-type')
            ctx['save-to'] = target_decoration.get('save-to')
            ctx['out-dir'] = output_path
            logger.info('\t ctx: {}'.format(ctx))
            split_into_files_02(output_path, template_genai_output, ctx)
        
        return None
    
    def fw(self):
        self.validateConfig()  
        self.process()
        self.generate()
    
    def targetSetup(self):
        self.validateConfig()  
        self.process()
        self.decorate()
        
        
