import aiohttp
import asyncio
from loguru import logger
import json
from colorama import init

init(autoreset=True)

class TheOrder:
    def __init__(self):
        self.base_url = "https://sp-odyssey-api.playnation.app/api"
        self.session = None
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/json",
            "Origin": "https://story-protocol-odyssey-tele.playnation.app",
            "Referer": "https://story-protocol-odyssey-tele.playnation.app/",
            "Sec-Ch-Ua": '"Not A;Brand";v="99", "Chromium";v="124", "Google Chrome";v="124"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Linux; U; Android 4.0.2; en-us; Galaxy Nexus Build/ICL53F) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"
        }

        # Configure Loguru without additional in-line color codes
        logger.remove()
        logger.add(
            lambda msg: print(msg, end=""),  # No newline between logs
            format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
            colorize=True,
            enqueue=True,
            backtrace=False,
            diagnose=False
        )

    def print_banner(self):
        banner = """
        ┏━━━━┳┓╋╋╋╋╋┏━━━┓╋╋╋┏┓╋╋╋╋╋┏━━━┓╋╋┏┓╋╋╋╋╋┏━┓    Auto KoniStory Bot
        ┃┏┓┏┓┃┃╋╋╋╋╋┃┏━┓┃╋╋╋┃┃╋╋╋╋╋┃┏━┓┃╋╋┃┃╋╋╋╋╋┃┏┛    Modified by @yogschannel
        ┗┛┃┃┗┫┗━┳━━┓┃┃╋┃┣━┳━┛┣━━┳━┓┃┃╋┃┣━━┫┗━┳━━┳┛┗┓
        ╋╋┃┃╋┃┏┓┃┃━┫┃┃╋┃┃┏┫┏┓┃┃━┫┏┛┃┗━┛┃━━┫┏┓┃┏┓┣┓┏┛
        ╋╋┃┃╋┃┃┃┃┃━┫┃┗━┛┃┃┃┗┛┃┃━┫┃╋┃┏━┓┣━━┃┃┃┃┏┓┃┃┃
        ╋╋┗┛╋┗┛┗┻━━┛┗━━━┻┛┗━━┻━━┻┛╋┗┛╋┗┻━━┻┛┗┻┛┗┛┗┛
        """
        print(banner)
        logger.info("Starting BeeHarvest Bot...")

    async def create_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def get_auth(self, init_data, address):
        try:
            payload = {
                "address": address,
                "referralCode": "C20WJXJv8",
                "initData": init_data
            }
            
            async with self.session.post(f"{self.base_url}/account/login", json=payload) as response:
                if response.status != 200:
                    return None
                    
                data = await response.json()
                return {
                    "token": data["token"],
                    "username": data["info"]["telegramUsername"],
                    "points": data["attributes"]["point"]
                }
        except Exception as e:
            logger.opt(colors=True).error(f"<red>Authentication error:</red> {str(e)}")
            return None

    async def get_tasks(self, token):
        try:
            headers = {**self.headers, "Authorization": f"Bearer {token}"}
            async with self.session.get(f"{self.base_url}/task/history", headers=headers) as response:
                if response.status == 200:
                    tasks = await response.json()
                    return [task["id"] for task in tasks if not task.get("submitted", False)]
                return []
        except Exception as e:
            logger.opt(colors=True).error(f"<red>Error getting tasks:</red> {str(e)}")
            return []

    async def clear_task(self, token, task_id):
        try:
            headers = {**self.headers, "Authorization": f"Bearer {token}"}
            payload = {
                "taskId": task_id,
                "extrinsicHash": "",
                "network": ""
            }
            async with self.session.post(f"{self.base_url}/task/submit", json=payload, headers=headers) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    return True, None
                elif response.status == 400 and "Task already submitted" in str(response_data.get("error", "")):
                    return True, "already_submitted"
                return False, None
        except Exception as e:
            logger.opt(colors=True).error(f"<red>Error clearing task:</red> {str(e)}")
            return False, None

    async def process_account(self, init_data, address):
        try:
            auth_data = await self.get_auth(init_data, address)
            if not auth_data:
                logger.opt(colors=True).error("<red>Failed to authenticate account</red>")
                return False

            logger.opt(colors=True).info(f"<cyan>Successfully logged in as {auth_data['username']} | Points: {auth_data['points']}</cyan>")
            
            tasks = await self.get_tasks(auth_data['token'])
            if not tasks:
                logger.opt(colors=True).info(f"<yellow>No pending tasks for {auth_data['username']}</yellow>")
                return True

            for task_id in tasks:
                success, status = await self.clear_task(auth_data['token'], task_id)
                if success:
                    msg = "Task already completed" if status == "already_submitted" else "Successfully cleared task"
                    logger.opt(colors=True).info(f"<yellow>{msg}</yellow> {task_id} for {auth_data['username']}")
                else:
                    logger.opt(colors=True).warning(f"<red>Failed to clear task</red> {task_id} for {auth_data['username']}")
                
                await asyncio.sleep(2)
            
            return True
            
        except Exception as e:
            logger.opt(colors=True).error(f"<red>Error processing account:</red> {str(e)}")
            return False

    async def run(self):
        try:
            self.print_banner()
            await self.create_session()
            
            with open('data.txt', 'r') as f_data, open('address.txt', 'r') as f_address:
                accounts = f_data.read().splitlines()
                addresses = f_address.read().splitlines()

            total_accounts = len(accounts)
            
            for i, (account, address) in enumerate(zip(accounts, addresses), 1):
                logger.opt(colors=True).info(f"<cyan>Processing account {i}/{total_accounts}</cyan>")
                success = await self.process_account(account, address)
                
                if i < total_accounts:
                    status = "Successfully processed" if success else "Failed to process"
                    logger.opt(colors=True).info(f"<yellow>{status} account. Waiting 3 seconds...</yellow>")
                    await asyncio.sleep(3)
            
            logger.opt(colors=True).success(f"<green>Finished processing all {total_accounts} accounts</green>")
            
        finally:
            await self.close_session()

if __name__ == "__main__":
    bot = TheOrder()
    asyncio.run(bot.run())
