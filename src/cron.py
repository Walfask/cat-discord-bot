import aiocron

from actions import send_random_image


def setup_cron(client):
    @aiocron.crontab("0 9 * * *")
    async def cron_send_pic():
        await send_random_image(client)
