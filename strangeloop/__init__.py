from .prompt import prompt
from .tool import tool
from . import utils

async def arun_json_output(llm, prompt):
    return utils.parse_json_reply(await llm(prompt))
