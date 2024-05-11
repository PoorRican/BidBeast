from models import Job
from functors.EmbeddingManager import EmbeddingManager


def global_generate_embeddings():
    """ Generate embeddings for all jobs in db """
    results = Job.table.select('id, desc').execute()
    jobs = results.data

    EmbeddingManager.generate_embeddings(jobs)
