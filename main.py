import discord
from discord import app_commands,utils
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
from datetime import datetime
import os


load_dotenv()

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

sunucu_adi = "Sunucu adınız"

bot_id = 1208950394043236383

server_id = 1208868393265135636

kayitsiz_role_id = 1208871478389510245
staff_role_id = 1208929592493088818
isim_onay_role_id = 1208955791302860870

emoji_log_channel_id = 1208946529763594250
isim_onay_channel_id = 1208930976261214328
message_log_channel_id = 1208965568800096306
on_voice_chat_join_channel_id = 1208971148541304862
on_voice_chat_leave_channel_id = 1208972664220426250
kayit_odasi_id = 1208929467645304842
kayitsiz_sohbet_id = 1208929329975791676
destek_cagir_channel_id = 1208934748647325736
destek_bekleme_channel_id = 1208933993031016459
hosgeldiniz_channel_id = 1208939073989779486
gorusuruz_channel_id = 1208939099839402034


class ticket_launcher(discord.ui.View):
    global sunucu_adi
    def __init__(self) -> None:
        super().__init__(timeout = None)
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 600, commands.BucketType.member)
    
    @discord.ui.button(label = "Bilet oluştur!", style = discord.ButtonStyle.blurple, custom_id = "ticket_button")
    async def ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        interaction.message.author = interaction.user
        retry = self.cooldown.get_bucket(interaction.message).update_rate_limit()
        if retry: return await interaction.response.send_message(f"Biraz yavaş ol! {round(retry, 1)} saniye sonra tekrar dene!", ephemeral = True)
        ticket = utils.get(interaction.guild.text_channels, name = f"ticket-{interaction.user.name.lower().replace(' ', '-')}-{interaction.user.discriminator}")
        if ticket is not None: await interaction.response.send_message(f"Zaten açık bir biletiniz var. {ticket.mention}!", ephemeral = True)
        else:
            if type(client.ticket_mod) is not discord.Role: 
                client.ticket_mod = interaction.guild.get_role(staff_role_id)
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel = False),
                interaction.user: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
                interaction.guild.me: discord.PermissionOverwrite(view_channel = True, send_messages = True, read_message_history = True), 
                client.ticket_mod: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
            }
            try: channel = await interaction.guild.create_text_channel(name = f"ticket-{interaction.user.name}-{interaction.user.discriminator}", overwrites = overwrites, reason = f"Ticket for {interaction.user}")
            except: return await interaction.response.send_message("Ticket oluşturma işlemi başarısız `manage_channels` permine sahip olduğuna emin ol!", ephemeral = True)
            await channel.send(f"{client.ticket_mod.mention}, {interaction.user.mention} Adlı kişi ticket oluşturdu.", view = main())
            await interaction.response.send_message(f"{channel.mention} Adlı odada biletini oluşturdum!", ephemeral = True)

class confirm(discord.ui.View):
    global sunucu_adi
    def __init__(self) -> None:
        super().__init__(timeout = None)
        
    @discord.ui.button(label = "Confirm", style = discord.ButtonStyle.red, custom_id = "confirm")
    async def confirm_button(self, interaction, button):
        try: await interaction.channel.delete()
        except: await interaction.response.send_message("Kanalı silme işlemi başarısız `manage_channels` permine sahip olduğundan emin ol!", ephemeral = True)

class main(discord.ui.View):
    global sunucu_adi
    def __init__(self) -> None:
        super().__init__(timeout = None)
    
    @discord.ui.button(label = "Bileti kapat", style = discord.ButtonStyle.red, custom_id = "kapat")
    async def close(self, interaction, button):
        embed = discord.Embed(title = "Bileti kapatmak istediğine emin misin?", color = discord.Colour.blurple())
        await interaction.response.send_message(embed = embed, view = confirm(), ephemeral = True)

    @discord.ui.button(label = "Transcript", style = discord.ButtonStyle.blurple, custom_id = "transcript")
    async def transcript(self, interaction, button):
        await interaction.response.defer()
        if os.path.exists(f"{interaction.channel.id}.md"):
            return await interaction.followup.send("Bir transcript zaten oluşturuluyor!", ephemeral = True)
        with open(f"{interaction.channel.id}.md", 'a', encoding='utf-8') as f:  # UTF-8 kodlaması belirtildi
            f.write(f"# Transcript of {interaction.channel.name}:\n\n")
            async for message in interaction.channel.history(limit=None, oldest_first=True):
                created = datetime.strftime(message.created_at, "%m/%d/%Y at %H:%M:%S")
                if message.edited_at:
                    edited = datetime.strftime(message.edited_at, "%m/%d/%Y at %H:%M:%S")
                    f.write(f"{message.author} on {created}: {message.clean_content} ({edited} Tarihinde düzenlendi.)\n")
                else:
                    f.write(f"{message.author} on {created}: {message.clean_content}\n")
            generated = datetime.now().strftime("%m/%d/%Y at %H:%M:%S")
            f.write(f"\n*{generated} tarihinde {client.user} tarafından oluşturuldu*\n*Zaman formatı: GG/AA/YY*\n*Saat Dilimi: UTC*")
        with open(f"{interaction.channel.id}.md", 'rb') as f:
            await interaction.followup.send(file=discord.File(f, f"{interaction.channel.name}.md"))
        os.remove(f"{interaction.channel.id}.md")

    
class aclient(discord.Client):
    global sunucu_adi
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents = intents)
        self.synced = False #we use this so the bot doesn't sync commands more than once
        self.added = False
        self.ticket_mod = staff_role_id

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced: #check if slash commands have been synced 
            await tree.sync(guild = discord.Object(id=server_id)) #guild specific: leave blank if global (global registration can take 1-24 hours)
            self.synced = True
        if not self.added:
            self.add_view(ticket_launcher())
            self.add_view(main())
            self.added = True
        print(f"We have logged in as {self.user}.")

client = aclient()
tree = app_commands.CommandTree(client)

@tree.command(guild = discord.Object(id=server_id), name = 'ticket', description='Ticket sistemi oluşturur.') #guild specific slash command
@app_commands.default_permissions(manage_guild = True)
@app_commands.checks.cooldown(3, 60, key = lambda i: (i.guild_id))
@app_commands.checks.bot_has_permissions(manage_channels = True)
async def ticketing(interaction: discord.Interaction):
    embed = discord.Embed(title = "Bilet oluşturmak için tıkla!", color = discord.Colour.blue())
    await interaction.channel.send(embed = embed, view = ticket_launcher())
    await interaction.response.send_message("Ticket sistemi başlatıldı!", ephemeral = True)

@tree.command(guild = discord.Object(id=server_id), name = 'kapat', description="Ticket'ı kapatır") #guild specific slash command
@app_commands.checks.bot_has_permissions(manage_channels = True)
async def close(interaction: discord.Interaction):
    if "ticket-for-" in interaction.channel.name:
        embed = discord.Embed(title = "Bu bileti kapatmak istediğine eminmisin?", color = discord.Colour.blurple())
        await interaction.response.send_message(embed = embed, view = confirm(), ephemeral = True)
    else: await interaction.response.send_message("Bu bir ticket değil!", ephemeral = True)

@tree.command(guild = discord.Object(id=server_id), name = 'ekle', description="Ticket'a bir kişiyi daha ekler") #guild specific slash command
@app_commands.describe(user = "Bu kullanıcı seni ticket'a eklemek istiyor")
@app_commands.default_permissions(manage_channels = True)
@app_commands.checks.cooldown(3, 20, key = lambda i: (i.server_id, i.user.id))
@app_commands.checks.bot_has_permissions(manage_channels = True)
async def add(interaction: discord.Interaction, user: discord.Member):
    if "ticket-for-" in interaction.channel.name:
        await interaction.channel.set_permissions(user, view_channel = True, send_messages = True, attach_files = True, embed_links = True)
        await interaction.response.send_message(f"{user.mention} Adlı kullanıcı başarı ile ticket'a eklendi. {interaction.user.mention}!")
    else: await interaction.response.send_message("Bu bir ticket değil!", ephemeral = True)

@tree.command(guild = discord.Object(id=server_id), name = 'sil', description="Bir kullanıcıyı ticket'tan siler") #guild specific slash command
@app_commands.describe(user = "Bu kullanıcı seni ticket'tan silmek istiyor.")
@app_commands.default_permissions(manage_channels = True)
@app_commands.checks.cooldown(3, 20, key = lambda i: (i.server_id, i.user.id))
@app_commands.checks.bot_has_permissions(manage_channels = True)
async def remove(interaction: discord.Interaction, user: discord.Member):
    if "ticket-for-" in interaction.channel.name:
        if type(client.ticket_mod) is not discord.Role: client.ticket_mod = interaction.guild.get_role(staff_role_id)
        if client.ticket_mod not in interaction.user.roles:
            return await interaction.response.send_message("Bunun için yetkin yok!", ephemeral = True)
        if client.ticket_mod not in user.roles:
            await interaction.channel.set_permissions(user, overwrite = None)
            await interaction.response.send_message(f"{user.mention} Adlı kullanıcı ticket'tan başarı ile silindi. {interaction.user.mention}!", ephemeral = True)
        else: await interaction.response.send_message(f"{user.mention} bir moderator!", ephemeral = True)
    else: await interaction.response.send_message("Bu bir ticket değil!", ephemeral = True)

@tree.command(guild = discord.Object(id=server_id), name = 'transcript', description='Bir transcript oluşturur.') #guild specific slash command
async def transcript(interaction: discord.Interaction): 
    if "ticket-for-" in interaction.channel.name:
        await interaction.response.defer()
        if os.path.exists(f"{interaction.channel.id}.md"):
            return await interaction.followup.send(f"Bir transcript zaten oluşturuluyor!", ephemeral = True)
        with open(f"{interaction.channel.id}.md", 'a') as f:
            f.write(f"# Transcript of {interaction.channel.name}:\n\n")
            async for message in interaction.channel.history(limit = None, oldest_first = True):
                created = datetime.strftime(message.created_at, "%m/%d/%Y at %H:%M:%S")
                if message.edited_at:
                    edited = datetime.strftime(message.edited_at, "%m/%d/%Y at %H:%M:%S")
                    f.write(f"{message.author} on {created}: {message.clean_content} (Edited at {edited})\n")
                else:
                    f.write(f"{message.author} on {created}: {message.clean_content}\n")
            generated = datetime.now().strftime("%m/%d/%Y at %H:%M:%S")
            f.write(f"\n*Generated at {generated} by {client.user}*\n*Date Formatting: MM/DD/YY*\n*Time Zone: UTC*")
        with open(f"{interaction.channel.id}.md", 'rb') as f:
            await interaction.followup.send(file = discord.File(f, f"{interaction.channel.name}.md"))
        os.remove(f"{interaction.channel.id}.md")
    else: await interaction.response.send_message("Bu bir bilet değil!", ephemeral = True)

@tree.context_menu(name = "Open a Ticket", guild = discord.Object(id=server_id))
@app_commands.default_permissions(manage_guild = True)
@app_commands.checks.cooldown(3, 20, key = lambda i: (i.server_id, i.user.id))
@app_commands.checks.bot_has_permissions(manage_channels = True)
async def open_ticket_context_menu(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.defer(ephemeral = True)
    ticket = utils.get(interaction.guild.text_channels, name = f"ticket-{user.name.lower().replace(' ', '-')}-{user.discriminator}")
    if ticket is not None: await interaction.followup.send(f"{user.mention} adlı kullanıcının zaten {ticket.mention} adlı bir bileti var!", ephemeral = True)
    else:
        if type(client.ticket_mod) is not discord.Role: 
            client.ticket_mod = interaction.guild.get_role(staff_role_id)
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel = False),
            user: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel = True, send_messages = True, read_message_history = True), 
            client.ticket_mod: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
        }
        try: channel = await interaction.guild.create_text_channel(name = f"ticket-for-{user.name}-{user.discriminator}", overwrites = overwrites, reason = f"{user} Adlı kullanıcı için {interaction.user} Tarafından bir ticket oluşturuldu.")
        except: return await interaction.followup.send("Ticket oluşturma işlemi başarısız `manage_channels` permine sahip olduğuna emin ol!", ephemeral = True)
        await channel.send(f"{interaction.user.mention} created a ticket for {user.mention}!", view = main())   
        await interaction.followup.send(f"{user.mention} Senin için {channel.mention} adlı ticket'ı oluşturdum!", ephemeral = True)

@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        return await interaction.response.send_message(error, ephemeral = True)
    elif isinstance(error, app_commands.BotMissingPermissions):
        return await interaction.response.send_message(error, ephemeral = True)
    else:
        await interaction.response.send_message("Bir hata oluştu!", ephemeral = True)
        raise error

@client.event
async def on_ready():
    global tree
    await tree.sync(guild=discord.Object(id=server_id))
    print("Bot hazır.")

@client.event
async def on_reaction_add(reaction:discord.Reaction,member:discord.Member):
    global client,emoji_log_channel_id,isim_onay_channel_id,isim_onay_role_id,bot_id,server_id,staff_role_id
    global sunucu_adi
    server = client.get_guild(server_id)
    emote = reaction.emoji
    emoteownername = member.name
    emoteowner = member
    emoteowneravatar = member.avatar
    emoteownerid = member.id
    kanal = reaction.message.channel
    messageowner = reaction.message.author
    message = reaction.message
    kanalid = reaction.message.channel.id
    emoji_log_channel = client.get_channel(emoji_log_channel_id)
    isim_onay_role = server.get_role(isim_onay_role_id)
    staff_role = server.get_role(staff_role_id)
    embed = discord.Embed(title="Emoji Log",color=0x90EE90)
    embed.set_thumbnail(url=emoteowneravatar)
    embed.set_footer(text=sunucu_adi)
    embed.add_field(name="Emoji:", value=emote,inline=False)
    embed.add_field(name="Emoji Basan Kişi:", value=emoteownername,inline=False)
    embed.add_field(name="Emoji Basan Kişinin ID:", value=emoteownerid,inline=False)
    embed.add_field(name="Emoji Basılan kanal:", value=kanal.mention,inline=False)
    embed.add_field(name="Emoji Basılan Kanalın Id'SI:", value=kanalid,inline=False)
    await emoji_log_channel.send(embed=embed)
    if kanalid == isim_onay_channel_id:
        await message.add_reaction("✅")
    if kanalid == isim_onay_channel_id and emote == "✅":
        if emoteowner.id == bot_id:
            print("Bot onaylamaya çalıştı.")
        elif staff_role in emoteowner.roles:
            await messageowner.add_roles(isim_onay_role)
            await message.author.edit(nick=f"{message.content.title()}")
            await message.author.send("IC Isim isteğin başarı ile onaylandı sunucuya giriş sağlayabilirsin.")
            print(f"Onaylama işlemi başarılı {messageowner.name} Adlı kişiye başarı ile Onay rolu verildi")
        else:
            print(f"Birisi onaylamaya çalıştı fakat rolu yoktu. {emoteowner.name}")
    if kanalid == isim_onay_channel_id and emote == "❎":
        if emoteownerid == bot_id:
            print("Bot reddetmeye çalıştı")
        else:
            await message.author.send("IC Isim isteğin reddedildi lütfen baştan gir.")

@client.event
async def on_member_join(member:discord.Member):
    global hosgeldiniz_channel_id
    global gorusuruz_channel_id
    global kayitsiz_role_id
    global client
    global server_id
    global sunucu_adi
    server = client.get_guild(server_id)
    hosgeldiniz_channel = server.get_channel(hosgeldiniz_channel_id)
    gorusuruz_channel = server.get_channel(gorusuruz_channel_id)
    kayitsiz_role = server.get_role(kayitsiz_role_id)
    embed = discord.Embed(title="Sunucuya birisi katıldı.",color=0x90EE90)
    embed.set_thumbnail(url=member.avatar)
    embed.set_footer(text=sunucu_adi)
    embed.add_field(name=f"Birisi sunucuya katıldı:", value=member.mention,inline=False)
    embed.add_field(name="kişinin hesabı oluşturduğu tarih:", value=member.created_at.date(),inline=False)
    embed.add_field(name="kişinin sunucuya katıldığı tarih:", value=member.joined_at.date(),inline=False)
    await member.add_roles(kayitsiz_role)
    await hosgeldiniz_channel.send(embed=embed)
    await member.send(f"Hoşgeldiniz 👋")

@client.event
async def on_member_remove(member:discord.Member):
    global hosgeldiniz_channel_id
    global gorusuruz_channel_id
    global kayitsiz_role_id
    global client
    global server_id
    global sunucu_adi
    server = client.get_guild(server_id)
    gorusuruz_channel = server.get_channel(gorusuruz_channel_id)
    embed = discord.Embed(title="Birisi sunucudan ayrıldı.",color=0x90EE90)
    embed.set_thumbnail(url=member.avatar)
    embed.set_footer(text=sunucu_adi)
    embed.add_field(name=f"Birisi sunucudan ayrıldı:", value=member.mention,inline=False)
    embed.add_field(name="kişinin hesabı oluşturduğu tarih:", value=member.created_at.date(),inline=False)
    embed.add_field(name="kişinin sunucuya katıldığı tarih:", value=member.joined_at.date(),inline=False)
    await gorusuruz_channel.send(embed=embed)

@client.event
async def on_message(message:discord.Message):
    global client,emoji_log_channel_id,isim_onay_channel_id,isim_onay_role_id,bot_id,destek_bekleme_channel_id
    global client
    global server_id
    global message_log_channel_id
    global destek_cagir_channel_id
    global sunucu_adi
    server = client.get_guild(server_id)
    destek_bekleme_channel = server.get_channel(destek_bekleme_channel_id)
    destek_cagir_channel = server.get_channel(destek_cagir_channel_id)
    isim_onay_channel = server.get_channel(isim_onay_channel_id)
    message_log_channel = server.get_channel(message_log_channel_id)
    embed = discord.Embed(title="Mesaj log",color=0x90EE90)
    embed.set_thumbnail(url=message.author.avatar)
    embed.set_footer(text=sunucu_adi)
    embed.add_field(name="Mesaj içeriği:", value=message.content,inline=False)
    embed.add_field(name="Mesajı yazan kişinin discord ismi:", value=message.author.name,inline=False)
    embed.add_field(name="Mesajı yazan kişinin discord id'si:", value=message.author.id,inline=False)
    embed.add_field(name="Mesajın yazıldığı kanal:",value=message.channel.mention,inline=False)
    embed.add_field(name="Mesajın yazıldığı kanalın id'si:",value=message.channel.id,inline=False)
    embed.add_field(name="Mesajı yazan kişinin hesabı oluşturduğu tarih:", value=message.author.created_at.date(),inline=False)
    embed.add_field(name="Mesajı yazan kişinin sunucuya katıldığı tarih:", value=message.author.joined_at.date(),inline=False)
    if message.author.id == bot_id:
        if message.channel.id != destek_cagir_channel.id or message.channel.id != destek_bekleme_channel.id:
            return
        else:
            print("Bot, destek_cagir_channel kanalında mesaj gönderdi.")
    else:
        await message_log_channel.send(embed=embed)
    if message.channel.id == isim_onay_channel_id:
        await message.add_reaction("✅")
        await message.add_reaction("❎")

@client.event
async def on_voice_state_update(member:discord.Member,before:discord.VoiceState,after:discord.VoiceState):
    global on_voice_chat_leave_channel_id
    global on_voice_chat_join_channel_id
    global server_id
    global client
    global kayit_odasi_id
    global kayitsiz_sohbet_id
    global staff_role_id
    global sunucu_adi
    server = client.get_guild(server_id)
    on_voice_chat_join_channel = server.get_channel(on_voice_chat_join_channel_id)
    on_voice_chat_leave_channel = server.get_channel(on_voice_chat_leave_channel_id)
    kayit_odasi = server.get_channel(kayit_odasi_id)
    kayitsiz_sohbet = server.get_channel(kayitsiz_sohbet_id)
    staff_role = server.get_role(staff_role_id)
    if before.channel is None and after.channel is not None:
        if after.channel.id == kayit_odasi.id:
            kayitGeldi = discord.Embed(title="Kayıt Geldi",color=0x90EE90)
            kayitGeldi.set_thumbnail(url=member.avatar)
            kayitGeldi.set_footer(text=sunucu_adi)
            kayitGeldi.add_field(name="Kayıt odası:",value=after.channel.mention,inline=False)
            kayitGeldi.add_field(name="Kayıt odasının discord idsi:",value=after.channel.id,inline=False)
            kayitGeldi.add_field(name="Kayıt odasına katılan kişinin discord ismi:", value=member.name,inline=False)
            kayitGeldi.add_field(name="Kayıt odasına katılan kişinin discord id'si:", value=member.id,inline=False)
            kayitGeldi.add_field(name="Kayıt odasına katılan kişinin hesabı oluşturduğu tarih:", value=member.created_at.date(),inline=False)
            kayitGeldi.add_field(name="Kayıt odasına katılan kişinin sunucuya katıldığı tarih:", value=member.joined_at.date(),inline=False)
            await kayitsiz_sohbet.send(staff_role.mention)
            await kayitsiz_sohbet.send(embed=kayitGeldi)
        embedKatıldı = discord.Embed(title="Ses kanalı log",color=0x90EE90)
        embedKatıldı.set_thumbnail(url=member.avatar)
        embedKatıldı.set_footer(text=sunucu_adi)
        embedKatıldı.add_field(name="Katılınan Kanal:",value=after.channel.mention,inline=False)
        embedKatıldı.add_field(name="Katılınan Kanal'ın idsi:",value=after.channel.id,inline=False)
        embedKatıldı.add_field(name="Kanala katılan kişinin discord ismi:", value=member.name,inline=False)
        embedKatıldı.add_field(name="Kanala katılan kişinin discord id'si:", value=member.id,inline=False)
        embedKatıldı.add_field(name="Kanala katılan kişinin hesabı oluşturduğu tarih:", value=member.created_at.date(),inline=False)
        embedKatıldı.add_field(name="Kanala katılan kişinin sunucuya katıldığı tarih:", value=member.joined_at.date(),inline=False)
        await on_voice_chat_join_channel.send(embed=embedKatıldı)
    elif before.channel is not None and after.channel is None:
        embedAyrildi = discord.Embed(title="Ses kanalı log",color=0x90EE90)
        embedAyrildi.set_thumbnail(url=member.avatar)
        embedAyrildi.set_footer(text=sunucu_adi)
        embedAyrildi.add_field(name="Ayrılınan kanal:",value=before.channel.mention,inline=False)
        embedAyrildi.add_field(name="Ayrılınan kanal'ın id'si:",value=before.channel.id,inline=False)
        embedAyrildi.add_field(name="Kanal'dan ayrılan kişinin discord ismi:", value=member.name,inline=False)
        embedAyrildi.add_field(name="Kanal'dan ayrılan kişinin discord id'si:", value=member.id,inline=False)
        embedAyrildi.add_field(name="Kanal'dan ayrılan kişinin hesabı oluşturduğu tarih:", value=member.created_at.date(),inline=False)
        embedAyrildi.add_field(name="Kanal'dan ayrılan kişinin sunucuya katıldığı tarih:", value=member.joined_at.date(),inline=False)
        await on_voice_chat_leave_channel.send(embed=embedAyrildi)

@tree.command(name="destek-cagir",description="Bir kişiyi destek bekleme odasına çağırır.",guild=discord.Object(id=server_id))
async def destek_cagir(interaction: discord.Interaction, kisi: discord.Member, neden: str):
    global staff_role_id
    global destek_cagir_channel_id
    global client
    global server
    global destek_bekleme_channel_id
    global sunucu_adi
    server = client.get_guild(server_id)
    staff_role = server.get_role(staff_role_id)
    destek_cagir_channel = server.get_channel(destek_cagir_channel_id)
    destek_bekleme_channel = server.get_channel(destek_bekleme_channel_id)
    if staff_role in interaction.user.roles:
        embed = discord.Embed(title=f"{interaction.user.name} Adlı yetkili {kisi.name} Adlı kişiyi destek çağırdı",color=0x90EE90)
        embed.set_thumbnail(url=kisi.avatar)
        embed.set_footer(text=sunucu_adi)
        embed.add_field(name="Destek bekleme kanalı:", value=destek_bekleme_channel.mention,inline=False)
        embed.add_field(name="Destek çağırma kanalı:", value=destek_cagir_channel   .mention,inline=False)
        embed.add_field(name="Destek çağıran yetkili:",value=interaction.user.name,inline=False)
        embed.add_field(name="Destek çağıran yetkili discord id'si:",value=interaction.user.id,inline=False)
        embed.add_field(name="Destek çağırılan kişi:",value=kisi.mention,inline=False)
        embed.add_field(name="Destek çağırılan kişinin discord idsi:",value=kisi.id,inline=False)
        embed.add_field(name="Kişinin destek çağırılma nedeni:",value=f"``{neden}``",inline=False)
        embed.add_field(name="Kişinin discorda katıldığı tarih:", value=kisi.created_at.date(),inline=False)
        embed.add_field(name="Kişinin sunucuya katıldığı tarih:", value=kisi.joined_at.date(),inline=False)
        await destek_cagir_channel.send(kisi.mention)
        await destek_cagir_channel.send(embed=embed)
        await kisi.send(f"Destek çağırıldın. https://discord.com/channels/1208868393265135636/1208933993031016459 \n\nÇağırılma nedenin ``{neden}``")
        await interaction.response.send_message(f"İşlem başarılı {kisi.name} Adlı kişi başarı ile desteğe çağırıldı.",ephemeral=True)
    else:
        await interaction.response.send_message("Bu komutu kullanmak için yetkin yok.",ephemeral=True)

client.run(os.getenv('DISCORD_BOT_TOKEN'))