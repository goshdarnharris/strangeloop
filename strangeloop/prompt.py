import sys
from . import utils
import ice.trace

MODEL_COST_MAP = {
    "text-davinci-003": 1,
    "gpt-3.5-turbo": 0.1,
}

class Prompt(object):
    def __init__(self, llm, func):
        self.llm = llm
        self.prompt_name = func.__name__ if hasattr(func, "__name__") else repr(func)
        self.call_prompt = func
    async def run(self,  *prompt_args, **prompt_kwargs):
        async def agenerate(prompt):
            trimmed = utils.dedent(prompt)
            result = await self.llm.agenerate([trimmed])
            
            total_tokens = result.llm_output.get("token_usage", 0).get(
                "total_tokens", 0
            )
            davinci_equivalent = int(
                MODEL_COST_MAP.get(self.llm.model_name, 0) * total_tokens
            )
            if davinci_equivalent > 0:
                ice.trace.add_fields(davinci_equivalent_tokens=davinci_equivalent)
            
            response = result.generations[0][0].text
            return response
        
        #Hack for ice tracing
        agenerate.__name__ = self.prompt_name

        return await self.call_prompt(ice.trace.trace(agenerate), *prompt_args, **prompt_kwargs)
    def __call__(self, *prompt_args, **prompt_kwargs):
        return self.run(*prompt_args, **prompt_kwargs)

def prompt(func):
    def make_prompt(llm):
        return Prompt(llm, func)
    return make_prompt