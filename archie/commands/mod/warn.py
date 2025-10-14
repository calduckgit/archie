import discord
from discord.ext import commands
import json
import os
import uuid

class WarnSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warn_data_path = "warnings.json"

        if not os.path.exists(self.warn_data_path) or os.path.getsize(self.warn_data_path) == 0:
            with open(self.warn_data_path, "w") as f:
                json.dump({}, f)


        try:
            with open(self.warn_data_path, "r") as f:
                self.warnings = json.load(f)
        except json.JSONDecodeError:
            self.warnings = {}
            with open(self.warn_data_path, "w") as f:
                json.dump(self.warnings, f)


    def save_warnings(self):
        with open(self.warn_data_path, "w") as f:
            json.dump(self.warnings, f, indent=4)

    @commands.command(name="warn", aliases=["w"])
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str):
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if not member:
            embed = discord.Embed(
                title="Error: no member specified.",
                description="You cannot warn thin air — please mention a user or their ID.\n\n**Did you mean?**\n`$warn @user/ID [reason]`",
                color=discord.Color.orange(),
            )
            embed.set_footer(text=f"User: {ctx.author}", icon_url=ctx.author.avatar.url)
            embed.timestamp = discord.utils.utcnow()
            await ctx.send(embed=embed)
            return

        if guild_id not in self.warnings:
            self.warnings[guild_id] = {}
        if user_id not in self.warnings[guild_id]:
            self.warnings[guild_id][user_id] = []

        warn_code = str(uuid.uuid4())[:8]

        self.warnings[guild_id][user_id].append({"code": warn_code, "reason": reason})
        self.save_warnings()

        embed = discord.Embed(
            title="Success: user warned.",
            description=f"The user {member.mention} has been warned with ID `{warn_code}`.\n\n" +
            f"**Reason:**\n```{reason}```\n" +
            "> **Was this a mistake?**\n> You can delete this specific warning with: `$delwarn @user/ID [warn ID]`",
            color=discord.Color.green(),
        )
        embed.set_footer(text=f"User: {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)

    @commands.command(name="warnings", aliases=["warns"])
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, ctx, member: discord.Member):
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id in self.warnings and user_id in self.warnings[guild_id]:
            user_warnings = self.warnings[guild_id][user_id]
            if user_warnings:
                warning_list = "\n".join(f"`{warning['code']}`: {warning['reason']}" for warning in user_warnings)
                embed = discord.Embed(
                    title="Retrived: user warnings",
                    description=f"Below are all the up-to-date warnings of the user: {member.mention}\n\n> **Note:**\n> You can delete a specific warning with: `$delwarn @user/ID [warn ID]`",
                    color=discord.Color.purple(),
                )
                embed.add_field(name="Warnings", value=warning_list, inline=False)
                embed.set_footer(text=f"User: {ctx.author}", icon_url=ctx.author.avatar.url)
                embed.timestamp = discord.utils.utcnow()

            else:
                embed = discord.Embed(
                    title="Error: no warnings found.",
                    description=f"The user {member.mention} has no warnings.",
                    color=discord.Color.orange(),
                )
                embed.set_footer(text=f"User: {ctx.author}", icon_url=ctx.author.avatar.url)
                embed.timestamp = discord.utils.utcnow()

        else:
            embed = discord.Embed(
                title="Error: no warnings found.",
                description=f"The user {member.mention} has no warnings.",
                color=discord.Color.orange(),
            )
            embed.set_footer(text=f"User: {ctx.author}", icon_url=ctx.author.avatar.url)
            embed.set_author(name="Warnings", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)

    @commands.command(name="clearwarnings", aliases=["clearwarns"])
    @commands.has_permissions(manage_messages=True)
    async def clearwarnings(self, ctx, member: discord.Member):
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id in self.warnings and user_id in self.warnings[guild_id]:
            self.warnings[guild_id][user_id] = []
            self.save_warnings()
            embed = discord.Embed(
                title="Success: warnings cleared.",
                description=f"All local-wide warnings for {member.mention} have been deleted.",
                color=discord.Color.green(),
            )
            embed.set_footer(text=f"User: {ctx.author}", icon_url=ctx.author.avatar.url)
            embed.timestamp = discord.utils.utcnow()

        else:
            embed = discord.Embed(
                title="Error: no warnings found.",
                description=f"The user {member.mention} has no warnings to clear.",
                color=discord.Color.orange(),
            )
            embed.set_footer(text=f"User: {ctx.author}", icon_url=ctx.author.avatar.url)
            embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)

    @commands.command(name="delwarn", aliases=["deletewarn"])
    @commands.has_permissions(manage_messages=True)
    async def delwarn(self, ctx, member: discord.Member, code: str):
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id in self.warnings and user_id in self.warnings[guild_id]:
            user_warnings = self.warnings[guild_id][user_id]

            for warning in user_warnings:
                if warning["code"] == code:
                    user_warnings.remove(warning)
                    self.save_warnings()

                    embed = discord.Embed(
                        title="Success: warning deleted.",
                        description=f"The warning `{code}` for {member.mention} has been deleted locally.\n\n**Reason:**\n```{warning['reason']}```",
                        color=discord.Color.green(),
                    )
                    embed.set_footer(text=f"User: {ctx.author}", icon_url=ctx.author.avatar.url)
                    embed.timestamp = discord.utils.utcnow()
                    await ctx.send(embed=embed)
                    return

            embed = discord.Embed(
                title="Error: warn code not found",
                description=f"The warning code `{code}` has not been found for {member.mention}.\n\n> **Double check the warn code:**\n> There could of been a mistype, so view all warnings with `$warnings @user/ID` and double-check if the warn code matches.",
                color=discord.Color.orange(),
            )
            embed.set_footer(text=f"User: {ctx.author}", icon_url=ctx.author.avatar.url)
            embed.timestamp = discord.utils.utcnow()
        else:
            embed = discord.Embed(
                title="Error: no warnings found.",
                description=f"The user {member.mention} has no warnings to clear.",
                color=discord.Color.orange(),
            )

        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(WarnSystem(bot))