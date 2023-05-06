import strangeloop

# @strangeloop.tool(
#     name = "remember", 
#     description = "search your memory for relevant information. your input should be in the form of a question."
# )
# def remember(google_cse_id, google_api_key):
#     search = GoogleSearchAPIWrapper(google_cse_id = google_cse_id, google_api_key = google_api_key)
#     async def call(query):
#         return search.run(query)
#     return call

@strangeloop.prompt
async def agent(llm, memory, user_prompt, max_iterations = 3):
    context = await memory.context()
    prompt = f"""
    You are a conversational AI language model. You are friendly and curious.
    You have a short term memory of about 4000 words. If you want to remember something older than that, you can think about it.
    Given a prompt from a human, select one action and generate an input to the action.

    You can select from the following actions:
    * think: try to remember something in your long term memory. your input can be a question or a search query.
    * reply: respond to the user's prompt.
    
    To select your action, generate a JSON object with the following format:
    ```
    {{
      "reasoning": "your step-by-step reasoning for your selection and input",
      "action": "your selected action, must be one of [think, reply]",
      "input": "your input to the selected action"
    }}
    ```

    Begin!

    Short term memory:
    {context}

    Prompt:
    {user_prompt}

    Action:
    ```
    """

    response = await strangeloop.arun_json_output(llm, prompt)
    
    await memory.store_thought(f"The user said '{user_prompt}'")

    for _ in range(max_iterations):
        if response.action == "think":
            await memory.store_thought(f"I decided to think about '{response.input}'. {response.reasoning}")
            remembered = await memory.summarize_query(response.input, 20)
            if not remembered:
                await memory.store_thought(f"I thought about '{response.input}', but I didn't remember anything.")
            else:
                await memory.store_thought(f"I thought about '{response.input}', and remembered: {remembered}")
        elif response.action == "reply":
            await memory.store_thought(f"I replied '{response.input}'. {response.reasoning}")
            return response.input
        
    await memory.store_thought(f"I couldn't come up with a good response to the user's prompt.")
    return "beep boop error"
