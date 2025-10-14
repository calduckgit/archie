import asyncio
import discord
from discord.ext import commands
import discord.utils

class ClearCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="clear", aliases=["purge"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, amount: int):
        if amount <= 0:
            embed = discord.Embed(
                title="Error: invalid number specified",
                description="You must provide a **positive** integer number of messages to delete.",
                color=discord.Color.orange(),
            )
            embed.set_footer(text=f"User: {ctx.author}", icon_url=getattr(ctx.author.avatar, "url", None))
            embed.timestamp = discord.utils.utcnow()
            await ctx.send(embed=embed, delete_after=10)
            return

        confirm_embed = discord.Embed(
            title="Wait: confirmation required!",
            description=f"Are you sure you want to delete `{amount}` messages?\n> *Use the green `Confirm` button to proceed or the red `Cancel` button to abort.*",
            color=discord.Color.yellow(),
        )
        confirm_embed.set_footer(text=f"User: {ctx.author}", icon_url=getattr(ctx.author.avatar, "url", None))
        confirm_embed.timestamp = discord.utils.utcnow()

        class ConfirmView(discord.ui.View):
            def __init__(self, timeout=30):
                super().__init__(timeout=timeout)
                self.value = None

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
            async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user != ctx.author:
                    await interaction.response.send_message(
                        "Oops, sorry! This is for the command author only.", ephemeral=True
                    )
                    return
                self.value = True
                self.stop()

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
            async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user != ctx.author:
                    await interaction.response.send_message(
                        "Oops, sorry! This is for the command author only.", ephemeral=True
                    )
                    return
                self.value = False
                self.stop()

        view = ConfirmView()
        confirm_message = await ctx.send(embed=confirm_embed, view=view)

        await view.wait()

        if view.value is None:
            try:
                await confirm_message.delete()
            except Exception:
                pass
            timeout_embed = discord.Embed(
                title="Error: timeout.",
                description="Confirmation timed out because of no response from the user — no messages were deleted.",
                color=discord.Color.orange(),
            )
            timeout_embed.set_footer(text=f"User: {ctx.author}", icon_url=getattr(ctx.author.avatar, "url", None))
            timeout_embed.timestamp = discord.utils.utcnow()
            await ctx.send(embed=timeout_embed, delete_after=10)
            return

        if view.value:
            try:
                deleted = await ctx.channel.purge(limit=amount + 1)
                count_deleted = max(0, len(deleted) - 1)
                success_embed = discord.Embed(
                    title="Success: messages cleared.",
                    description=f"Deleted the following amount of messages:\n```{count_deleted}```",
                    color=discord.Color.green(),
                )
                success_embed.set_footer(text=f"User: {ctx.author}", icon_url=getattr(ctx.author.avatar, "url", None))
                success_embed.timestamp = discord.utils.utcnow()
                confirmation_message = await ctx.send(embed=success_embed)

                await confirmation_message.delete(delay=10)

                try:
                    await confirm_message.delete()
                except Exception:
                    pass
            except discord.Forbidden:
                embed = discord.Embed(
                    title="Error: no permission.",
                    description="I require the `Manage Messages` permission to delete messages.",
                    color=discord.Color.red(),
                )
                embed.set_footer(text=f"User: {ctx.author}", icon_url=getattr(ctx.author.avatar, "url", None))
                embed.timestamp = discord.utils.utcnow()
                await ctx.send(embed=embed, delete_after=10)
            except discord.HTTPException as e:
                embed = discord.Embed(
                    title="Error: error.",
                    description=f"An error occurred while deleting messages: {e}",
                    color=discord.Color.red(),
                )
                embed.set_footer(text=f"User: {ctx.author}", icon_url=getattr(ctx.author.avatar, "url", None))
                embed.timestamp = discord.utils.utcnow()
                await ctx.send(embed=embed, delete_after=10)

        else:
            try:
                await confirm_message.delete()
            except Exception:
                pass
            cancel_embed = discord.Embed(
                title="Error: user cancelled",
                description="The user cannceled the message deletion — no messages were deleted.",
                color=discord.Color.orange(),
            )
            cancel_embed.set_footer(text=f"User: {ctx.author}", icon_url=getattr(ctx.author.avatar, "url", None))
            cancel_embed.timestamp = discord.utils.utcnow()
            await ctx.send(embed=cancel_embed, delete_after=10)

    @clear.error
    async def clear_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Error: missing amount.",
                description="An amount was not specified so no messages were deleted.\n> **Tip:**\n> The correct usage is: `$clear <amount>`",
                color=discord.Color.orange(),
            )
            embed.set_footer(text=f"User: {ctx.author}", icon_url=getattr(ctx.author.avatar, "url", None))
            embed.timestamp = discord.utils.utcnow()
            await ctx.send(embed=embed, delete_after=10)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Bad argument",
                description="Please provide a valid integer for the amount.",
                color=discord.Color.orange(),
            )
            embed.set_footer(text=f"User: {ctx.author}", icon_url=getattr(ctx.author.avatar, "url", None))
            embed.timestamp = discord.utils.utcnow()
            await ctx.send(embed=embed, delete_after=10)
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Error: no user permissions",
                description="You need the `Manage Messages` permission to use this command.",
                color=discord.Color.orange(),
            )
            embed.set_footer(text=f"User: {ctx.author}", icon_url=getattr(ctx.author.avatar, "url", None))
            embed.timestamp = discord.utils.utcnow()
            await ctx.send(embed=embed, delete_after=10)
        else:
            embed = discord.Embed(
                title="Error: error.",
                description=f"An unexpected error occurred: `{error}`",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed, delete_after=10)

async def setup(bot: commands.Bot):
    await bot.add_cog(ClearCog(bot))
