import strangeloop
import asyncio
import json
import textwrap
from collections import namedtuple
import chromadb
import ice.trace
from . import prompts, entry


#a claim has:
# a kind (inference, deduction, induction, abduction, etc.)
# a list of evidence
# a rating

# Ideas
# build relationships between ingested data ("I think this is related to that because ...")

#FIXME: vector store needs to be versioned, need to handle backwards compatibility scenarios

@ice.trace.trace
class Memory(object):
    def __init__(self, llm, embedder, filename):
        self.llm = llm
        self.embedder = embedder
        self.memory_filename = filename
        self.n_questions_ingest = 3


        # self.ingest_research_questions = prompts.gen_questions_from_data(self.llm)
        # self.check_evidence = prompts.verify_claim_against_data(self.llm)
        self.summarize_thoughts = prompts.summarize_thoughts(self.llm)
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.create_collection(name = "memory")

        with open(self.memory_filename, 'w', encoding = 'utf-8') as f:
            pass

    async def store_entries(self, entries):
        self.collection.add(
            documents = [e.content for e in entries],
            ids = [e.ident for e in entries],
            metadatas = [entry.to_metadata(e) for e in entries]
        )
        with open(self.memory_filename, 'a+', encoding = 'utf-8') as f:
            for e in entries:
                f.write(f"{e.content}\n")

    async def recent_entries(self, n):
        offset = self.collection.count() - n
        if offset < 0:
            n = self.collection.count()
            offset = 0
        results = self.collection.get(
            include = ["documents"],
            offset = offset, 
            limit = n
        )
        return results["documents"]
    
    async def query_entries(self, query, n, **kwargs):
        results = self.collection.query(query_texts = [query],
            n_results = n,
            include = ["documents"],
            where = kwargs
        )
        return results["documents"]

    async def store_thought(self, content):
        await self.store_entries([entry.Thought(content)])

    async def context(self):
        thoughts = await self.recent_entries(20)
        s = await self.summarize_thoughts(thoughts)
        return s
    
    async def summarize_query(self, query, n, **kwargs):
        entries = await self.query_entries(query, n, **kwargs)
        if len(entries) > 0:
            s = await self.summarize_thoughts(entries)
            return s
        return None
    
    async def query_claims(self, question, n):
        return await self.query_entries(question, n)

    async def ingest_data(self, document):
        # Question based research:
        #  ask a question
        #  research the question (memory, database, online, etc) - maybe an agent
        #    research process generates evidence
        #  try to answer the question using the evidence
        #  judge whether or not the answer is well supported
        # This process generates evidenced claims, and thoughts about the research process.

        # How do I dedupe claims?

        # Claim checking
        #  ask questions about it
        #  do question based research
        #  check if the claim is well evidenced

        # Claim insertion
        #  to begin with, just put it into memory


        await self.store_thought()
        # gen_claims_from_data = prompts.gen_claims_from_data(self.llm)
        # check_claim_against_data = prompts.check_claim_against_data(self.llm)
        # gen_infer_from_claims_and_data


        # #Store thoughts as we go so context will be affected

        # # Summarize data
        # # Make claims based on data
        # # Ask questions of the data
        # #  use them to find existing claims
        # # Make new claims based on data + related existing claims, if any
        # # Check claims against evidence
        # #  ask questions
        # #  search for claims + data related to the claim
        # #  check for support/refute
        # #  connect claims/data in graph/note support
        # # Score claims
        # #  ???


        


        # await self.store_thought(f'I read part of <filename>, and indexed it as <embedding>. It said:\n```{data}```')

        # await self.store_thought(f"I think it's about <topic> because <reason>.")
        
        # context = await self.context()
        # research_questions = await self.ingest_research_questions(data, request, context)
        
        # for question in research_questions:
        #     await self.store_thought(f"While reading, a question occurred to me: {question}")

        # claims = await asyncio.gather(*[self.query_claims(question, n = 3) for question in research_questions])

        # #At some point, I need to break claims into assumptions and check those assumptions

        # checks = await asyncio.gather(*[self.check_evidence(data, claim) for claim in claims])
        
        # for claim, check in zip(claims, checks):
        #     if check.assessment != "unrelated":
        #         await self.store_thought(f"I checked my claim that {claim} against what I just read. "
        #             f"I feel {check.confidence} that this new information {check.assessment} my claim. "
        #         )
        #     else:
        #         await self.store_thought(f"I checked my claim that {claim} against what I just read. "
        #             f"I feel {check.confidence} that this new information is {check.assessment} to my claim. "
        #         )

    async def ingest_goal(self, goal):
        await self.store_thought(f"I have resolved to {goal}")

    async def ingest_action(self, action):
        pass

