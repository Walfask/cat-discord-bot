import aiocron

from actions import send_image_from_db


def setup_cron(client):
    @aiocron.crontab("0 9 * * *")
    async def cron_send_pic():
        await send_image_from_db(client)
