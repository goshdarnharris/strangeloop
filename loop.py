import os
os.environ["OUGHT_ICE_HOST"] = "localhost"
os.environ["OUGHT_ICE_PORT"] = "5555"
import langchain_visualizer

import returns
import strangeloop
import strangeloop.models
import strangeloop.memory.critical
import string
import asyncio

from langchain.utilities import GoogleSearchAPIWrapper

@strangeloop.prompt
def researcher(tools):
    tool_descriptions = "\n        ".join([f"> {tool.name}: {tool.description}" for tool in tools])
    async def call(llm, question):
        prompt = f"""You are a researcher. You are creative and curious, and you hold facts in high regard.
        Given a question and a context, you use one of the tools available to you research the question.
        
        You have access to the following tools:
        <tools>
        {tool_descriptions}

        To use a tool, reply with the following syntax:
        <thought> your step-by-step reasoning for using this tool with this specific input
        <tool> the tool to use; must be one of the tools listed above
        <input> the input to the tool

        Begin!

        <context> I already looked up the pinout for the 2n7002.

        <question> {question}
        <thought> """
        
        return await llm(prompt)
    return call

@strangeloop.tool(
    name = "digikey_search", 
    description = "useful for looking up part specifications, prices, and availability"
)
def digikey_search(google_cse_id, google_api_key):
    search = GoogleSearchAPIWrapper(google_cse_id = google_cse_id, google_api_key = google_api_key)
    async def call(query):
        return search.run(query)
    return call

@strangeloop.tool(
    name = "part_expert", 
    description = "ask about the functionality, pinning, characteristics, or behaviour of a component. be sure to include a part number in your query."
)
def part_expert():
    async def call(query):
        return "oh no, I don't know anything about parts yet!"
    return call


async def main():
    # database = part_expert()

    # r = researcher(strangeloop.models.davinci_003(), [digikey, database])
    # tool = await r("which pin is drain on the 2n7002?")
    # print(tool)

    mem = strangeloop.memory.critical.memory(
        strangeloop.models.davinci_003(temperature = 0.8), 
        strangeloop.models.huggingface_embed(),
        "memory.txt"
    )
    
    await mem.ingest_goal("fulfill the request: which pin on the AOZ2153 is used to tune its switching frequency?")
    await mem.ingest_data(
        data = """EQI-30 is a Green Product voltage regulator, critical component in any component of a lifesupport, device, or system whose failure to perform can be reasonably expected to cause the failure of the lifesupport device or system, or to affect its safety or effectiveness. It is part of the AOZ2153 series and is marked with the code ADEM. It is designed to regulate the peak inductor ripple current, which can be calculated by the formula: 

ICO_RMSIL
12----------=(13)

There is not a relationship between the input capacitor RMS current and voltage conversion ratio.

The power dissipation of the inductor can be approximately calculated by output current and DCR of inductor and output current. The thermal performance of the AOZ2153EQI-30 is strongly affected by the PCB layout. Extra care should be taken by users during design process to ensure that the IC will operate under the recommended environmental conditions. Several layout tips are listed below for the best electric and thermal performance: 

1. The LX pins and pad are connected to internal low side switch drain. They are low resistance thermal conduction path and most noisy switching node. Connected a large copper plane to LX pin to help thermal dissipation.
2. The IN pins""",
        request = "which pin on the AOZ2153 is used to tune its switching frequency?"
    )

    #now I have async LLM functions that I can compose
    #I need to integrate tracing
    #Then I can start to implement bits

if __name__ == '__main__':
    langchain_visualizer.visualize(main)
