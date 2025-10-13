import discord
from discord.ext import commands
from discord import app_commands
import discord.utils

class KickCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="kick", aliases=["k"])
    async def kick_prefix(self, ctx, member: discord.Member = None):
        if not member:
            embed = discord.Embed(
                title="Error: no member specified.",
                description="You cannot kick thin air — please mention a user or their ID.\n\n> **Did you mean?**\n> `$kick @user/ID`",
                color=discord.Color.orange()
            )
            embed.set_footer(text=f"User: {ctx.author}", icon_url=ctx.author.avatar.url)
            embed.timestamp = discord.utils.utcnow()
            await ctx.send(embed=embed)
            return
        
        if not ctx.guild.me.guild_permissions.kick_members:
            embed = discord.Embed(
                title="Error: insufficient permissions.",
                description="Please ensure I have the `Kick Members` permission.\n\n> **Tip:**\n> Check my permissions by right-clicking me and selecting `Server Settings` > `Roles`. Make sure this is enabled for my highest role.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"User: {ctx.author}", icon_url=ctx.author.avatar.url)
            embed.timestamp = discord.utils.utcnow()
            await ctx.send(embed=embed)
            return
        
        if member.top_role >= ctx.guild.me.top_role or member == ctx.guild.owner:
            embed = discord.Embed(
                title="Error: permissions error.",
                description="This user cannot be kicked — make sure their top role is above mine.\n\n> **Tip:**\n> Make sure my top role is above the user you are trying to kick.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"User: {ctx.author}", icon_url=ctx.author.avatar.url)
            embed.timestamp = discord.utils.utcnow()
            await ctx.send(embed=embed)
            return
        
        if member == ctx.author:
            embed = discord.Embed(
                title="Error: cannot kick yourself.",
                description="We love having you around here, so we stopped you from kicking yourself.",
                color=discord.Color.orange()
            )
            embed.set_footer(text=f"User: {ctx.author}", icon_url=ctx.author.avatar.url)
            embed.timestamp = discord.utils.utcnow()
            await ctx.send(embed=embed)
            return
        
        try:
            reason = None
            if ctx.message.content:
                parts = ctx.message.content.split()
                if "?r" in parts:
                    r_index = parts.index("?r")
                    reason = " ".join(parts[r_index + 1:]) if r_index + 1 < len(parts) else None

            await member.kick(reason=reason)
            embed = discord.Embed(
                title="Success: user kicked.",
                description=f"Successfully kicked {member.mention} from the server.\n\n" +
                            (f"**Reason:**\n```{reason}```" if reason else "") +
                            "> **Note:**\n> The user has been kicked and will not be able to rejoin unless they are invited again.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"User: {ctx.author}", icon_url=ctx.author.avatar.url)
            embed.timestamp = discord.utils.utcnow()
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error: failed to kick user.",
                description=f"An error occurred while trying to kick the user: {e}",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"User: {ctx.author}", icon_url=ctx.author.avatar.url)
            embed.timestamp = discord.utils.utcnow()
            await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(KickCog(bot))