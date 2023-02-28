#this exists because I didn't begin the project with a virtual environment

import re

with open('../requirements.txt', 'r') as f:
    file_contents = f.read()
f.close()

regex = re.compile(r'.*@.*\n')

output = regex.sub('', file_contents)

# write the output string back to the requirements file
with open('../requirements.txt', 'w') as f:
    f.write(output)
f.close()