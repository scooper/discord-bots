import discord

token = 'NzYzMDQ0MjU5ODQ1NzY3MTk4.X3x-WA.2E8Nzb_d56jJuBt4LkoujwWcDXI'

class BotClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content} in channel {0.channel}'.format(message))

client = BotClient()
client.run(token)
