import re

code = '''
<paste the plaintext code here>
'''

# Split code into blocks between ```java and ``` 
code_blocks = re.split(r'(```java.*?```)', code, flags=re.DOTALL)

# Remove empty matches
code_blocks = [block for block in code_blocks if block]

# Write each block to a separate file
for i, block in enumerate(code_blocks):
    with open(f'File{i+1}.java', 'w') as f:
        f.write(block)
        