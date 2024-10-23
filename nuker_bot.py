import discord
from discord.ext import commands
import asyncio
from discord import app_commands
import os
from dotenv import load_dotenv

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all() )




@bot.command(name="nuke")
@commands.has_permissions(administrator=True)
async def nuke(ctx, max_channels: int = None, max_messages: int = None, spam_message: str = None, new_server_name: str = None, channel_name: str = None):
    # Check that all parameters are provided by the user
    if max_channels is None or max_messages is None or spam_message is None or new_server_name is None or channel_name is None:
        await ctx.send("Error: `!nuke <max_channels> <max_messages> <spam_message> <new serv name> <channel name>`.")
        return

    # Check that max_channels and max_messages are positive integers
    if max_channels < 1 or max_messages < 1:
        await ctx.send("Error: The number of channels and the number of messages must be greater than 0.")
        return

    excluded_channel_ids = ["The channels should not be deleted"]

    async def delete_channel(channel):
        if channel.name not in excluded_channel_ids:
            try:
                await channel.delete()
            except Exception:
                pass

    async def create_channel(i):
        # Use the channel name specified by the user with a number
        channel = await ctx.guild.create_text_channel(f"{channel_name}-{i + 1}")  
        for _ in range(max_messages):
            await channel.send(f"@everyone {spam_message}")  # Use the user-chosen message
            await asyncio.sleep(1)  # Pause to avoid API rate limits

    async def ban_members():
        for member in ctx.guild.members:
            if member != ctx.guild.owner and member != ctx.author and member.top_role < ctx.guild.me.top_role:
                try:
                    await member.ban(reason="Nuke the server.")
                except Exception:
                    pass

    try:
        # Change the server name to the one given by the user
        await ctx.guild.edit(name=new_server_name)
        await ban_members()

        # Delete all existing channels
        delete_tasks = [delete_channel(channel) for channel in ctx.guild.channels]
        await asyncio.gather(*delete_tasks)

        # Create the new channels
        create_tasks = [create_channel(i) for i in range(max_channels)]
        await asyncio.gather(*create_tasks)
    except Exception as e:
        print(f"Error occurred: {e}")  # Print errors to the console for debugging



















@bot.command(name="wipe")
@commands.has_permissions(administrator=True)
async def wipe(ctx, *excluded_channels):
    guild = ctx.guild  # Get the server
    delete_tasks = []

    for channel in guild.channels:
        # Check if the name or ID of the channel is in the exclusions
        if str(channel.name) not in excluded_channels and str(channel.id) not in excluded_channels:
            delete_tasks.append(channel.delete())
            await ctx.send("Done")

    try:
        await asyncio.gather(*delete_tasks)
    except Exception:
        pass



@bot.command(name="del")
@commands.has_permissions(administrator=True)
async def delete_channel(ctx, *, channel_identifiers: str = None):
    if channel_identifiers is None:
        await ctx.send("Please provide the name or ID of a channel to delete `!del <channel_name_1> <channel_name_2>`")
        return

    guild = ctx.guild
    channel_names = channel_identifiers.split()  # Split names by spaces
    deleted_channels = []
    not_found_channels = []

    for channel_identifier in channel_names:
        channel_to_delete = None
        if channel_identifier.isdigit():
            # Check if the identifier is a number, then try to find it by ID
            channel_to_delete = discord.utils.get(guild.channels, id=int(channel_identifier))
        else:
            # Otherwise, try to find by name
            channel_to_delete = discord.utils.get(guild.channels, name=channel_identifier)

        if channel_to_delete:
            await channel_to_delete.delete()
            deleted_channels.append(channel_to_delete.name)
        else:
            not_found_channels.append(channel_identifier)

    if deleted_channels:
        await ctx.send(f"The following channel(s) have been deleted: {', '.join(deleted_channels)}.")
    if not_found_channels:
        await ctx.send(f"The following channel(s) do not exist: {', '.join(not_found_channels)}.")









@bot.command(name="purge")
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount_of_msg: str = None):
    """Deletes a specified number of messages in the channel."""
    if amount_of_msg is None:
        await ctx.send("Please specify the number of messages to delete or type 'all' to delete all messages.")
        return

    if amount_of_msg.lower() == 'all':
        await ctx.channel.purge()  # Supprime tous les messages
        await ctx.send("All messages have been deleted.", delete_after=5)
        return

    try:
        amount_of_msg = int(amount_of_msg)  # Convertit en entier

        if amount_of_msg < 1:
            await ctx.send("The number of messages to delete must be greater than 0.")
            return
        
        # Supprime les messages mais garde le message de commande
        deleted = await ctx.channel.purge(limit=amount_of_msg + 1)  # +1 pour inclure le message de commande
        await ctx.send(f"{len(deleted) - 1} messages have been deleted.", delete_after=5)  # Soustrait 1 pour ne pas compter le message de commande

    except ValueError:
        await ctx.send("Please provide a valid number of messages to delete.")








@bot.command(name="hlp")
async def help(ctx):
    embed = discord.Embed(
        title="Available Commands ☽",
        description="__Here are the commands you can use:__",
        color=discord.Color.dark_gray()
    )

    embed.add_field(
        name="!nuke `!nuke <max_channels> <max_messages> <spam_message> <new serv name> <channel name>`",
        value="Deletes all channels, creates new ones, spams @everyone, bans members, and changes the server name.",
        inline=False
    )
    
    embed.add_field(
        name="!del `!del <channel_name> <channel_name2>...`",
        value="Deletes channel(s) by name or ID ⚠️ **If the name is a number, use the ID**.",
        inline=False
    )
    
    embed.add_field(
        name="!wipe `!wipe <exclusions...>`",
        value="Deletes all channels except those specified by name or ID.",
        inline=False
    )
    
    embed.add_field(
        name="!banall `!banall <exclusions...>`",
        value="Bans all members except those specified by name or ID.",
        inline=False
    )
    
    embed.add_field(
        name="!crt `!crt <name> <name2>...`",
        value="This command creates a channel/s.",
        inline=False
    )
    
    embed.add_field(
        name="!purge `!purge <number_of_messages or 'all'>`",
        value="Deletes a specified number of messages in the channel, or type 'all' to delete all messages.",
        inline=False
    )
    
    embed.add_field(
        name="!hlp `!hlp`",
        value="Shows this help message.",
        inline=False
    )
    
    embed.set_image(url="https://i.pinimg.com/originals/c6/f8/81/c6f881c0a0593a3c0e67cf258094396f.gif")
    
    await ctx.send(embed=embed)






@bot.command(name="banall")
@commands.has_permissions(administrator=True)
async def banall(ctx, *excluded_members):
    guild = ctx.guild  # Récupère le serveur
    ban_tasks = []
    not_found_members = []

    for excluded in excluded_members:
        # Vérifie si le membre spécifié existe dans le serveur
        member = discord.utils.get(guild.members, name=excluded) or discord.utils.get(guild.members, id=int(excluded) if excluded.isdigit() else None)
        
        if member:
            # Si le membre existe et n'est pas dans les exclusions
            if str(member.id) not in excluded_members:
                ban_tasks.append(member.ban())
        else:
            not_found_members.append(excluded)  # Ajouter à la liste si le membre n'est pas trouvé

    # Exécute toutes les tâches de bannissement
    if ban_tasks:
        await asyncio.gather(*ban_tasks)
        await ctx.send("Done")
    
    # Vérifie s'il y a des membres non trouvés
    if not_found_members:
        await ctx.send(f"The following {'member' if len(not_found_members) == 1 else 'members'} {'was' if len(not_found_members) == 1 else 'were'} not found in the server: {', '.join(not_found_members)}")


    try:
        await asyncio.gather(*ban_tasks)
    except:
        pass


@bot.command(name="crt")
@commands.has_permissions(manage_channels=True)
async def create_channel(ctx, *, channel_identifiers: str = None):
    if channel_identifiers is None:
        await ctx.send("Please enter the names of the channels `!crt <name1> <name2> ...`")
        return

    # Split the input into a list of channel names
    channel_names = channel_identifiers.split()

    # Create the channels in order
    created_channels = []
    for name in channel_names:
        new_channel = await ctx.guild.create_text_channel(name)
        created_channels.append(new_channel)

    await ctx.send(f"Created channel/s: {', '.join([channel.name for channel in created_channels])}")



@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Sorry, this command does not exist.")
    






tree = bot.tree  # Create a command tree for slash commands

@tree.command(name="nuke", description="Nukes the server and creates spam channels.")
@app_commands.checks.has_permissions(administrator=True)
async def nuke(interaction: discord.Interaction, 
                max_channels: int = 5, 
                max_messages: int = 5, 
                spam_message: str = "Hi cuties", 
                new_server_name: str = "Raid my Who?", 
                channel_name: str = "spam"):
    
    excluded_channel_ids = ["Les salons a pas suprr"]  # Channels not to delete

    async def delete_channel(channel):
        if channel.name not in excluded_channel_ids:
            try:
                await channel.delete()
            except Exception:
                pass

    async def create_channel(i):
        # Use the channel name specified by the user with a number
        channel = await interaction.guild.create_text_channel(f"{channel_name}-{i + 1}")
        for _ in range(max_messages):
            await channel.send(f"@everyone {spam_message}")  # Use the user-chosen message
            await asyncio.sleep(1)  # Pause to avoid API rate limits

    async def ban_members():
        for member in interaction.guild.members:
            if member != interaction.guild.owner and member != interaction.user and member.top_role < interaction.guild.me.top_role:
                try:
                    await member.ban(reason="Nuke du serveur.")
                except Exception:
                    pass

    try:
        # Change the server name to the one given by the user
        await interaction.guild.edit(name=new_server_name)
        await ban_members()

        # Delete all existing channels
        delete_tasks = [delete_channel(channel) for channel in interaction.guild.channels]
        await asyncio.gather(*delete_tasks)

        # Create the new channels
        create_tasks = [create_channel(i) for i in range(max_channels)]
        await asyncio.gather(*create_tasks)

        await interaction.response.send_message("Server nuked and channels created!", ephemeral=True)  # Feedback to user
    except Exception as e:
        print(f"Error occurred: {e}")  # Print errors to the console for debugging
        await interaction.response.send_message("An error occurred while nuking the server.", ephemeral=True)

# Remember to sync the commands tree with Discord
@bot.event
async def on_ready():
    await tree.sync()  # Sync slash commands with Discord
    print(f"Logged in as {bot.user.name}")






tree = bot.tree  # Create a command tree for slash commands

@tree.command(name="hlp", description="Shows the available commands.")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Available Commands ☽",
        description="__Here are the commands you can use:__",
        color=discord.Color.dark_gray()
    )

    embed.add_field(
        name="/nuke",
        value="Deletes all channels, creates new ones, spams @everyone, bans members, and changes the server name.\nUsage: `/nuke max_channels: <number> max_messages: <number> spam_message: <string> new_server_name: <string> channel_name: <string>`",
        inline=False
    )
    
    embed.add_field(
        name="/del",
        value="Deletes channel(s) by name or ID ⚠️ **If the name is a number, use the ID**.\nUsage: `/del channel_name channel_name2 ...`",
        inline=False
    )
    
    embed.add_field(
        name="/wipe",
        value="Deletes all channels except those specified by name or ID.\nUsage: `/wipe exclusion1 exclusion2 ...`",
        inline=False
    )
    
    embed.add_field(
        name="/banall",
        value="Bans all members except those specified by name or ID.\nUsage: `/banall exclusion1 exclusion2 ...`",
        inline=False
    )
    
    embed.add_field(
        name="/crt",
        value="Creates channel(s).\nUsage: `/crt name name2 ...`",
        inline=False
    )
    
    embed.add_field(
        name="/purge",
        value="Deletes a specified number of messages in the channel, or type 'all' to delete all messages.\nUsage: `/purge number_of_messages` or `/purge all`.",
        inline=False
    )
    
    embed.add_field(
        name="/hlp",
        value="Shows this help message.",
        inline=False
    )
    
    embed.set_image(url="https://i.pinimg.com/originals/c6/f8/81/c6f881c0a0593a3c0e67cf258094396f.gif")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)  # Make the message ephemeral

# Remember to sync the commands tree with Discord
@bot.event
async def on_ready():
    await tree.sync()  # Sync slash commands with Discord
    print(f"Logged in as {bot.user.name}")




@tree.command(name="crt", description="Creates text channels.")
@app_commands.checks.has_permissions(manage_channels=True)
async def create_channel(interaction: discord.Interaction, channel_identifiers: str = None):
    if channel_identifiers is None or not channel_identifiers.strip():
        await interaction.response.send_message("Please provide the name of channel/s (e.g., `/crt name1 name2 ...`)", ephemeral=True)
        return

    # Split the input into a list of channel names
    channel_names = channel_identifiers.split()

    # Create the channels in order
    created_channels = []
    for name in channel_names:
        new_channel = await interaction.guild.create_text_channel(name)
        created_channels.append(new_channel)

    await interaction.response.send_message(f"Successfully created channel/s: {', '.join([channel.name for channel in created_channels])}!")  # Feedback to user


@tree.command(name="banall", description="Bans all members except those specified.")
@app_commands.checks.has_permissions(administrator=True)
async def banall(interaction: discord.Interaction, excluded_members: str = ""):
    guild = interaction.guild  # Get the guild
    ban_tasks = []
    not_found_members = []

    # Split the input string into a list of member names or IDs
    excluded_members_list = excluded_members.split()

    for excluded in excluded_members_list:
        # Check if the specified member exists in the server
        member = discord.utils.get(guild.members, name=excluded) or discord.utils.get(guild.members, id=int(excluded) if excluded.isdigit() else None)
        
        if member:
            # If the member exists and is not in exclusions
            if str(member.id) not in excluded_members_list:
                ban_tasks.append(member.ban(reason="Banned by the banall command."))
        else:
            not_found_members.append(excluded)  # Add to the list if the member is not found

    # Execute all ban tasks
    if ban_tasks:
        await asyncio.gather(*ban_tasks)
        await interaction.response.send_message("Done! The specified members have been banned.")
    else:
        await interaction.response.send_message("No members were banned. Please check the names provided.")

    # Check if there are not found members
    if not_found_members:
        await interaction.followup.send(f"The following {'member' if len(not_found_members) == 1 else 'members'} {'was' if len(not_found_members) == 1 else 'were'} not found in the server: {', '.join(not_found_members)}")


tree = bot.tree  # Create a command tree for slash commands

@tree.command(name="wipe", description="Deletes all channels except those specified.")
@app_commands.checks.has_permissions(administrator=True)
async def wipe(interaction: discord.Interaction, excluded_channels: str = None):
    guild = interaction.guild  # Get the server
    delete_tasks = []

    # Split the excluded channels into a list
    excluded_channels_set = set(excluded_channels.split()) if excluded_channels else set()

    for channel in guild.channels:
        # Check if the name or ID of the channel is in the exclusions
        if str(channel.name) not in excluded_channels_set and str(channel.id) not in excluded_channels_set:
            delete_tasks.append(channel.delete())

    if delete_tasks:  # Only attempt to gather tasks if there are any
        try:
            await asyncio.gather(*delete_tasks)
            await interaction.response.send_message("Done! All specified channels have been deleted.")
        except Exception as e:
            await interaction.response.send_message(f"An error occurred while deleting channels: {e}")
    else:
        await interaction.response.send_message("No channels were deleted because all were excluded.")

@bot.event
async def on_ready():
    await tree.sync()  # Sync slash commands with Discord
    print(f"Logged in as {bot.user}")






tree = bot.tree  # Create a command tree for slash commands

@tree.command(name="purge", description="Deletes a specified number of messages in the channel.")
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, amount_of_msg: str = None):
    """Deletes a specified number of messages in the channel."""
    
    if amount_of_msg is None:
        await interaction.response.send_message("Please specify the number of messages to delete or type 'all' to delete all messages.", ephemeral=True)
        return

    if amount_of_msg.lower() == 'all':
        deleted = await interaction.channel.purge()  # Delete all messages
        await interaction.response.send_message(f"All messages have been deleted. Total deleted: {len(deleted)}", delete_after=5)
        return

    try:
        amount_of_msg = int(amount_of_msg)  # Convert to integer

        if amount_of_msg < 1:
            await interaction.response.send_message("The number of messages to delete must be greater than 0.", ephemeral=True)
            return
        
        # Delete messages but keep the command message
        deleted = await interaction.channel.purge(limit=amount_of_msg + 1)  # +1 to include the command message
        await interaction.response.send_message(f"{len(deleted) - 1} messages have been deleted.", delete_after=5)  # Subtract 1 to not count the command message

    except ValueError:
        await interaction.response.send_message("Please provide a valid number of messages to delete.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("I do not have permission to delete messages in this channel.", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.response.send_message(f"An error occurred while trying to delete messages: {e}", ephemeral=True)


tree = bot.tree  # Create a command tree for slash commands

@tree.command(name="del", description="Deletes specified channels by name or ID.")
@app_commands.checks.has_permissions(administrator=True)
async def delete_channel(interaction: discord.Interaction, channel_identifiers: str = None):
    """Deletes specified channels by name or ID."""
    if channel_identifiers is None:
        await interaction.response.send_message("Please provide the name or ID of a channel to delete. Usage: `/del <channel_name_1> <channel_name_2>`", ephemeral=True)
        return

    guild = interaction.guild
    channel_names = channel_identifiers.split()  # Split names by spaces
    deleted_channels = []
    not_found_channels = []

    for channel_identifier in channel_names:
        channel_to_delete = None
        if channel_identifier.isdigit():
            # Check if the identifier is a number, then try to find it by ID
            channel_to_delete = discord.utils.get(guild.channels, id=int(channel_identifier))
        else:
            # Otherwise, try to find by name
            channel_to_delete = discord.utils.get(guild.channels, name=channel_identifier)

        if channel_to_delete:
            await channel_to_delete.delete()
            deleted_channels.append(channel_to_delete.name)
        else:
            not_found_channels.append(channel_identifier)

    if deleted_channels:
        await interaction.response.send_message(f"The following channel(s) have been deleted: {', '.join(deleted_channels)}.")
    if not_found_channels:
        await interaction.response.send_message(f"The following channel(s) do not exist: {', '.join(not_found_channels)}.", ephemeral=True)

@bot.event
async def on_ready():
    await tree.sync()  # Sync slash commands with Discord
    print(f"Logged in as {bot.user}")






        
bot.run("YOUR_TOKEN")