import sys
import json
from collections import namedtuple

def dedent(prompt):
    if not prompt:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = prompt.expandtabs().splitlines()

    def measure_indent(line):
        return len(line) - len(line.lstrip())
    
    #Use 2nd line to determine indent:
    indent = measure_indent(lines[1])
    
    trimmed = []
    if indent < sys.maxsize:
        for line in lines:
            line_indent = measure_indent(line)
            #If it has a greater or equal indent than the 2nd line, trim it:
            if line_indent >= indent:
                trimmed.append(line[indent:].rstrip())
            #Otherwise, keep it as-is:
            else:
                trimmed.append(line.rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)

def format_prompt(prompt, *args, **kwargs):
    return dedent(prompt).format(*args, **kwargs)

def parse_json_reply(reply):
    if reply:
        return json.loads(reply.strip('`'), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    else:
        return None
    
def make_bulleted_list(items, bullet = '*'):
    return '\n'.join(f'{bullet} {item}' for item in items)

def parse_bulleted_list(text, bullet = '*'):
    return [line.strip()[2:] for line in text.splitlines() if line.startswith(f'{bullet} ')]
