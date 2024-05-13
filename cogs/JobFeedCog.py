from typing import ClassVar, Union, NoReturn

import discord
from discord.ext import tasks
from discord.ext.commands import Cog

from functors.SearchManager import SearchManager
from models import Job
from utils import extract_jobs, handle_new_jobs


class JobFeedCog(Cog):
    searches: Union[SearchManager, None]
    user: discord.User
    cache: list[Job] = []

    def __init__(self, user: discord.User):
        self.user = user
        self.searches = SearchManager(user)

    async def cog_load(self):
        await self.enable_loop()

    @tasks.loop(minutes=5)
    async def fetch_feed(self):
        """ Fetch RSS feed and process new jobs """
        try:
            assert self.searches is not None
        except AssertionError:
            raise ValueError("`JobFeedCog` was not properly instantiated. `searches` is `None`")

        raw_feed = self.searches()
        new_jobs = extract_jobs(raw_feed)
        handled = handle_new_jobs(new_jobs)

        if handled:
            self.cache.extend(handled)
            await self.user.send("# Incoming Jobs\n"
                                 f"Good news! I found {len(handled)} job(s) you might be interested in.")
            await self.list_cache(handled)

    async def list_cache(self, jobs: Union[list[Job], None] = None) -> NoReturn:
        if jobs is None:
            jobs = self.cache
        if len(jobs):
            for index, job in enumerate(jobs):
                await self.user.send(job.summary_repr(index))
            await self.user.send("Use `!feed list <num>` to get details of a particular job.")
        else:
            await self.user.send("There are no jobs to show")

    async def list_details(self, index: int):
        count = len(self.cache)
        if count == 0:
            await self.user.send("Job cache is empty")
        if 0 < index <= count:
            index -= 1
            job = self.cache[index]
            for msg in job.detailed_repr():
                await self.user.send(msg)
        else:
            await self.user.send(f"Error: Please submit a number between 1 and {count}")

    def clear_cache(self) -> NoReturn:
        self.cache = []

    async def enable_loop(self):
        """Start the fetching RSS feed"""
        self.fetch_feed.start()
        await self.user.send("> Started to fetch RSS feeds")

    async def disable_loop(self):
        """Stop the fetching RSS feed"""
        self.fetch_feed.stop()
        await self.user.send("> Stopped fetching RSS feed")

    async def status(self, ctx):
        if self.fetch_feed.is_running():
            await ctx.send("> Fetching RSS feed")
        else:
            await ctx.send("> Not fetching RSS feed")
