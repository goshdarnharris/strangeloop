import strangeloop
import asyncio
import json
import textwrap
from collections import namedtuple
from .. import utils

@strangeloop.prompt
def generate_questions(n):
    async def call(llm, data, request, context):
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
    return call

@strangeloop.prompt
def evidence_check():
    async def call(llm, data, claim):
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
    return call

@strangeloop.prompt
def infer(n):
    async def call(llm, data, claims, context):
        claim_list = [f'* {c}\n' for c in claims]
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

    return call

@strangeloop.prompt
def summarize_thoughts():
    async def call(llm, thoughts):
        
        prompt = f"""
        Given {len(thoughts)} thoughts, write a 1 paragraph summary.

        Begin!

        Thoughts:
        {utils.make_bulleted_list(thoughts)}

        Summary:
        """
        return await llm(prompt)
    return call
#a claim has:
# a kind (inference, deduction, induction, abduction, etc.)
# a list of evidence
# a rating

# Ideas
# build relationships between ingested data ("I think this is related to that because ...")

class memory(object):
    def __init__(self, llm, embedder, filename):
        self.llm = llm
        self.embedder = embedder
        self.memory_filename = filename
        self.n_questions_ingest = 3

        self.ingest_research_questions = generate_questions(self.llm, self.n_questions_ingest)
        self.check_evidence = evidence_check(self.llm)
        self.summarize_thoughts = summarize_thoughts(self.llm)

        self.memory = []

        with open(self.memory_filename, 'w', encoding = 'utf-8') as f:
            pass

    def write_memory(self, content):
        self.memory.append(content)
        with open(self.memory_filename, 'a+', encoding = 'utf-8') as f:
            f.write(f"{content}\n")
    
    def recent_thoughts(self, n):
        return self.memory[-n:]

    async def context(self):
        s = await self.summarize_thoughts(self.recent_thoughts(20))
        # print(s)
        return s
    
    async def claim_query(self, question, k):
        return question

    async def ingest_data(self, data, request):
        self.write_memory(f'I read part of <filename>, and indexed it as <embedding>. It said:\n```{data}```')

        self.write_memory(f"I think it's about <topic> because <reason>.")
        
        context = await self.context()
        research_questions = await self.ingest_research_questions(data, request, context)
        
        for question in research_questions:
            self.write_memory(f"While reading, a question occurred to me: {question}")

        claims = await asyncio.gather(*[self.claim_query(question, k = 3) for question in research_questions])
        checks = await asyncio.gather(*[self.check_evidence(data, claim) for claim in claims])
        
        for claim, check in zip(claims, checks):
            if check.assessment != "unrelated":
                self.write_memory(f"I checked my claim that {claim} against what I just read. "
                    f"I feel {check.confidence} that this new information {check.assessment} my claim. "
                )
            else:
                self.write_memory(f"I checked my claim that {claim} against what I just read. "
                    f"I feel {check.confidence} that this new information is {check.assessment} to my claim. "
                )

    async def ingest_goal(self, goal):
        self.write_memory(f"I have resolved to {goal}")

    async def ingest_action(self, action):
        pass

