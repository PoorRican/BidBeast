from html import unescape
import re

from markdownify import markdownify
from postgrest.types import CountMethod

from db import SUPABASE
from helpers import retry_on_error
from models import Job, HourlyRange


def _extract_job(entry: dict) -> Job:
    """ Prepare RSS entry

    :param entry: extracts title and summary from RSS entry

    :return: combined title and summary
    """
    title = entry['title'].replace('- Upwork', '')
    summary = markdownify(entry['summary_detail']['value'])
    summary = unescape(summary)

    return Job(title=title, link=entry['link'], description=summary)


@retry_on_error()
def _extract_jobs(entries: list[dict]) -> list[Job]:
    """ Accept new `Job` objects from the raw RSS feed """
    jobs = [_extract_job(i) for i in entries]

    _titles = [i.title for i in jobs]
    _results = SUPABASE.table('potential_jobs') \
        .select('title', count=CountMethod.exact) \
        .in_('title', _titles) \
        .execute()
    duplicates_titles = [i['title'] for i in _results.data]

    incoming = []
    for job in jobs:
        if job.title not in duplicates_titles:
            incoming.append(job)
    print(f"Parsed {len(incoming)} jobs...")
    return incoming


def _store_job(jobs: list[Job]):
    """ Store job data in supabase """
    formatted = []
    for i in jobs:
        row = {
            'title': i.title,
            'desc': i.description,
            'link': i.link,
        }
        formatted.append(row)
    SUPABASE.table('potential_jobs').insert(formatted).execute()


def _handle_new_jobs(jobs: list[Job]) -> list[Job]:
    """ Process a given list of new jobs.

    Any processing of jobs should occur here.
    """
    if jobs:
        print(f"Found {len(jobs)} new jobs")
        _store_job(jobs)
        return jobs
    else:
        print("No new jobs...")


def _parse_hourly_range(job: Job) -> Job:
    """ Parse hourly rate from job description """
    if 'hourly rate' in job.description.lower():
        pattern = r"\$(\d+\.\d+)"
        matches = re.findall(pattern, job.description)

        # Convert the matches to float
        matches = [float(match) for match in matches]
        if len(matches) == 2:
            job.hourly_range = HourlyRange(start=matches[0], end=matches[1])
    return job


def extract_and_handle_jobs(entries: list[dict]) -> list[Job]:
    """ Extract and handle new jobs from the raw RSS feed """
    jobs = _extract_jobs(entries)

    # Parse hourly rate
    jobs = [_parse_hourly_range(i) for i in jobs]

    return _handle_new_jobs(jobs)
