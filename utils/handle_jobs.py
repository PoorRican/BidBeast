from typing import ClassVar

from postgrest import SyncRequestBuilder

from db import SUPABASE
from models import Job


def _store_job(jobs: list[Job]):
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
    SUPABASE.table('potential_jobs').insert(formatted).execute()


def handle_new_jobs(jobs: list[Job]) -> list[Job]:
    """ Process a given list of new jobs.
    """
    if jobs:
        print(f"Found {len(jobs)} new jobs")
        _store_job(jobs)
        return jobs
    else:
        print("No new jobs...")
