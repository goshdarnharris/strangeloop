import datetime

def to_metadata(entry):
    def check_key(key):
        return key not in ['content', 'ident'] and key[0] != '_'
    metadata = entry.__dict__
    return {k: v for k, v in metadata.items() if check_key(k)}

class Entry(object):
    def __init__(self, kind, content, timestamp = None):
        self.kind = kind
        self.ident = str(timestamp.isoformat()) if timestamp else str(datetime.datetime.now().isoformat())
        self.content = content

class Claim(Entry):
    def __init__(self, claim, reasoning_used, evidence):
        super().__init__(
            kind = "claim", 
            content = claim
        )
        self.reasoning = reasoning_used
        self.evidence = evidence

class Thought(Entry):
    def __init__(self, thought):
        super().__init__(
            kind = "thought", 
            content = thought
        )