from asyncio import gather

from functors.Summarizer import Summarizer
from models import Job
from functors.EmbeddingManager import EmbeddingManager


def global_generate_embeddings():
    """ Generate embeddings for all jobs in db """
    results = Job.table.select('id, desc').execute()
    jobs = results.data

    EmbeddingManager.generate_embeddings(jobs)


async def global_summarization():
    """ Generate summaries for all jobs in db """
    async def re_summarize(row: dict):
        summary = await Summarizer.chain.arun({'description': row['description']})
        Job.table.update({'summary': summary}).eq('id', row['id']).execute()

    results = Job.table.select('id, desc').execute()
    _jobs = results.data
    jobs = []
    for job in _jobs:
        jobs.append({'id': job['id'], 'description': job['desc']})

    print(f"Fetched {len(jobs)} rows")

    routines = []
    for job in jobs:
        routines.append(re_summarize(job))
    await gather(*routines)
