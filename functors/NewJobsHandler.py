from typing import ClassVar

from postgrest import SyncRequestBuilder

from db import SUPABASE
from models import Job


class NewJobsHandler(object):
    """ Handles new jobs by storing them in supabase.

    This is used by the `JobFeedCog` and is the primary method to handle, interact with, and manipulate incoming jobs.
    """
    _table: ClassVar[SyncRequestBuilder] = SUPABASE.table('potential_jobs')

    @classmethod
    def _store_job(cls, jobs: list[Job]):
        """ Store job data in supabase """
        formatted = []
        for i in jobs:
            row = {
                'id': str(i.id),
                'title': i.title,
                'desc': i.description,
                'link': i.link,
            }
            formatted.append(row)
        cls._table.insert(formatted).execute()

    @classmethod
    async def __call__(cls, jobs: list[Job]) -> list[Job]:
        """ Process a given list of new jobs.

        A summary and embeddings are generated. Additionally, feedback is automatically generated.
        Jobs which are evaluated to be viable are returned.
        """
        if jobs:
            print(f"Found {len(jobs)} new jobs")
            cls._store_job(jobs)
            return jobs
        else:
            print("No new jobs...")
