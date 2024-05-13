from typing import Union, Optional

from discord.ext.commands.bot import Bot
from discord.ext import commands

from cogs.BaseAuthenticatedCog import BaseAuthenticatedCog
from cogs.JobFeedCog import JobFeedCog


class MainCog(BaseAuthenticatedCog):
    bot: Bot
    job_feed: Union[JobFeedCog, None] = None

    def __init__(self, bot: Bot):
        super().__init__(None)
        print("Initializing MainCog")
        self.bot = bot

    @commands.command('connect')
    async def connect(self, ctx):
        """Connect the bot to the channel"""
        if self.user == ctx.author:
            await ctx.send("You're already connected silly!")
            return
        self.user = ctx.author

        await ctx.send("Gotcha...")

        # setup job feed
        self.job_feed = JobFeedCog(self.user)
        await self.bot.add_cog(self.job_feed)

    # Feed commands

    @commands.group('feed',
                    help='manage job searches')
    async def feed(self, ctx):
        if await self._check_user(ctx):
            await ctx.send("User is not authenticated")
            return

        if ctx.invoked_subcommand is None:
            await ctx.send("No sub-command given. Use `!help feed` to learn about available commands.")

    @feed.command('add',
                  aliases=['a'],
                  help='add RSS URL to poll group')
    async def add_search(self, ctx, *args):
        await self.job_feed.searches.add_url(args[0])

    @feed.command('remove',
                  aliases=['rm'],
                  help='remove RSS URL from poll group')
    async def remove_search(self, ctx, *args):
        await ctx.send("This function has not been implemented yet")

    @feed.command('searches',
                  aliases=['s'],
                  help='list current searches (RSS URLs)')
    async def list_searches(self, ctx):
        await ctx.send(f"Current searches:\n{self.job_feed.searches.feed_urls}")

    @feed.command('enable',
                  aliases=['e'],
                  help='enable background loop to look for and notify about relevant jobs')
    async def enable_feed(self, _: commands.Context):
        await self.job_feed.enable_loop()

    @feed.command('disable',
                  aliases=['d'],
                  help='disable background loop to look for and notify about relevant jobs')
    async def disable_feed(self, _: commands.Context):
        await self.job_feed.disable_loop()

    @feed.command('status',
                  aliases=['st'],
                  help='return status of background loop')
    async def feed_status(self, ctx):
        await self.job_feed.status(ctx)

    @feed.command('list',
                  aliases=['l'],
                  help='list all relevant jobs stored in cache')
    async def list_feed(self, _: commands.Context, number: Optional[int] = None):
        if number:
            await self.job_feed.list_details(number)
        else:
            await self.job_feed.list_cache()

    @feed.command('clear',
                  aliases=['c'],
                  help='clear current cache of relevant jobs')
    async def clear_feed(self, ctx):
        await self.job_feed.clear_cache()
