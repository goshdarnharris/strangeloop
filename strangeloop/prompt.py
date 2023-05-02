import sys
from . import utils
import ice.trace

class Prompt(object):
    def __init__(self, llm, func, args, kwargs):
        self.llm = llm
        self.prompt_name = func.__name__ if hasattr(func, "__name__") else repr(func)
        self.call_prompt = func(*args, **kwargs)
    async def run(self,  *prompt_args, **prompt_kwargs):
        async def agenerate(prompt):
            trimmed = utils.dedent(prompt)
            result = await self.llm.agenerate([trimmed])
            response = result.generations[0][0].text
            return response
        
        #Hack for ice tracing
        agenerate.__name__ = self.prompt_name

        return await self.call_prompt(ice.trace.trace(agenerate), *prompt_args, **prompt_kwargs)
    def __call__(self, *prompt_args, **prompt_kwargs):
        return self.run(*prompt_args, **prompt_kwargs)

def prompt(func):
    def make_prompt(llm, *args, **kwargs):
        return Prompt(llm, func, args, kwargs)
    return make_prompt