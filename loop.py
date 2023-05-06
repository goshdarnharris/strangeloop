import os
os.environ["OUGHT_ICE_HOST"] = "localhost"
os.environ["OUGHT_ICE_PORT"] = "5555"
import langchain_visualizer

import returns
import strangeloop
import strangeloop.models
import strangeloop.memory.critical
import strangeloop.agents.strangeloop
import string
import asyncio
import typer

from langchain.utilities import GoogleSearchAPIWrapper


async def conversation():
    mem = strangeloop.memory.critical.Memory(
        strangeloop.models.davinci_003(temperature = 0.1), 
        strangeloop.models.huggingface_embed(),
        "memory.txt"
    )

    agent = strangeloop.agents.strangeloop.agent(strangeloop.models.davinci_003(temperature = 0.8))

    while True:
        user_prompt = typer.prompt(">")
        response = await agent(mem, user_prompt)
        print(f"∞ {response}")
    

def main():
    langchain_visualizer.visualize(conversation)

if __name__ == '__main__':
    typer.run(main)
