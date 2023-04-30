
class Tool(object):
    def __init__(self, name, description, func):
        self.name = name
        self.description = description
        self.func = func
    async def __call__(self, *args, **kwargs):
        return await self.func(*args, **kwargs)

def tool(name, description):
    def decorate_func(func):
        def make_tool(*args, **kwargs):
            return Tool(name, description, func(*args, **kwargs))
        return make_tool
    return decorate_func