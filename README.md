# yaml file format
The below is the yaml file format

version : v1
kind : schema
metadata:
    description : "Generate database schema from the promots and save"
spec:
    chain: false
    prompts:
        -prompt:
            text : "What is the name of the application?"
            context:   """ 00000 """
            context:   """ 00001 """"
            output-dir : schema.sql
        -prompt:
            text : "What is the name of the application?"
            -context:   """ 00000 """
            -context:   """ 00001 """"