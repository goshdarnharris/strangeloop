import sys
from . import utils


class Prompt(object):
    def __init__(self, llm, func):
        self.llm = llm
        self.func = func
    async def run(self,  *prompt_args, **prompt_kwargs):
        async def agenerate(prompt):
            trimmed = utils.dedent(prompt)
            print("PROMPT", trimmed)
            result = await self.llm.agenerate([trimmed])
            response = result.generations[0][0].text
            print("RESPONSE", response)
            return response
        return await self.func(agenerate, *prompt_args, **prompt_kwargs)
    def __call__(self, *prompt_args, **prompt_kwargs):
        return self.run(*prompt_args, **prompt_kwargs)

def prompt(func):
    def make_prompt(llm, *args, **kwargs):
        return Prompt(llm, func(*args, **kwargs))
    return make_prompt