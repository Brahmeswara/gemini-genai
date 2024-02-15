import google.generativeai as genai
import os
from utils import Logger

logger = Logger('gemini_ai_assistant: ')

##genai.configure(api_key="AIzaSyDluMvWjaSjBjxzPti6d1FMoR-Saftfy9Q")

# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048000,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_NONE"
  },
]

class gemini_ai_assistant ():
    
    def __init__(self, ctx):
        self._ctx = ctx 
        self._modelInitilized = False
        self._response = None
        
    def _validate (self):
        if ( self._ctx == None ):
            raise Exception("Context is not set")
        
        if ( self._ctx.get('api_key') == None ):
            raise Exception("API Key is not set")
        
    def _initModel (self):
        self._validate()
        genai.configure(api_key=self._ctx.get('api_key'))
        self._model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)
        
        self._modelInitilized = True
  
    
    def generateContent01(self, prompt_parts):
        if ( self._modelInitilized == False ):
            self._initModel()
            
        self._response = self._model.generate_content(prompt_parts)
        return self._response 
    
    def getResponse(self):
        return self._response
        
    def printResponse(self):
        print(self._response)
      
    def generateContent(self, prompt_parts):
        #if ( self._modelInitilized == False ):
        self._initModel()
            
        res = ""
        try: 
          response = self._model.generate_content(prompt_parts)
          ##response.resolve()
          
          ##for chunk in response:
          ##  print('\n--- chunk --- ')
          ##  res = res + chunk.text
          ##  ##print(chunk.text)
          
          res = response.text
            
          self._response = res 
          
        except ValueError as verror:
          response.resolve()
          logger.error('error-1: {}'.format(verror))
          logger.error('promot_feedback: '.format(response.prompt_feedback))
          logger.error('error 1: parts: {}'.format(response.parts))
          logger.error('error-1: candidates: {}'.format(response.candidates))
          raise ValueError('error-1: {}'.format(verror))
        except Exception as e:
          logger.error('error-2: {}'.format(e))
          raise e
        
        return self._response

# this is for testing purposes at module level
if __name__ == "__main__":
    ##genai.configure(api_key="AIzaSyDluMvWjaSjBjxzPti6d1FMoR-Saftfy9Q")
    ctx = {}
    ctx['api_key'] = os.getenv('GENAI_API_KEY')
    
    ait = gemini_ai_assistant(ctx)
    
    prompt_parts = [
    "Given a typical order and products, please generate a database schema for h2 in-memory database ",
    ]   
    #res = ait.generateContent02(prompt_parts)
    #ait.printResponse()
    