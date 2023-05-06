import strangeloop
from . import entry
from ... import utils

@strangeloop.prompt
async def gen_questions_from_data(llm, data, request, context, n):
    prompt = f"""
    Given some context, some trusted information, and a request, {n} insightful questions that are answered by the information and related to the request.
    Respond using a JSON array in the following format:
    ```
    ["question 1", ...]
    ```

    Context: 
    {context}

    Information: 
    {data}

    Request: {request}

    Questions:
    ```"""
    return await strangeloop.arun_json_output(llm, prompt)

@strangeloop.prompt
async def check_claim_against_data(llm, data, claim):
    prompt = f"""
    Given some trusted information and a claim that may or may not be true, provide an assessment of whether the information supports the claim, refutes the claim, or is unrelated to the claim. Additionally, provide your logic step-by-step, and a rating of your confidence in your assessment. 
    Respond using a JSON object in the following format:

    ```
    {{
        "assessment": "[supports, refutes, unrelated]",
        "why": "your step-by-step logic for your assessment",
        "confidence": "[unsure, sure, confident, certain]"
    }}
    ```

    Begin!

    Information:
    {data}

    Claim: {claim}

    ```
    """

    return await strangeloop.arun_json_output(llm, prompt)

@strangeloop.prompt
async def gen_infer_from_claims_and_data(llm, data, claims, context, n):
    prompt = f"""
    Given some context, some trusted information, and a list of assertions, draw {n} new inferences from the trusted information.
    Respond using a JSON array in the following format:
    ```
    ["inference 1", ...]
    ```

    Begin!
    Context:
    {context}

    Information:
    {data}

    Assertions:
    {utils.make_bulleted_list(claims)}

    Inferences:
    ```
    """
    return await strangeloop.arun_json_output(llm, prompt)

@strangeloop.prompt
async def summarize_thoughts(llm, thoughts):        
    prompt = f"""
    Given {len(thoughts)} thoughts, write a 1 paragraph summary.

    Begin!

    Thoughts:
    {utils.make_bulleted_list(thoughts)}

    Summary:
    """
    return await llm(prompt)

@strangeloop.prompt
async def gen_claims_from_data(llm, data, n):
    prompt = f"""
    Provide factual statements based on the provided information. The information is trustworthy. Answer using a bulleted list of {n} one-sentence statements.

    Begin!

    Information:
    {data}

    {n} statements:
    * """
    return await llm(prompt)