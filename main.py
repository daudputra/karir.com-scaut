from src.controller.daily import DailyController
from src.controller.main_controller import MainController
from src.helper.mylog import log_message

import argparse
import asyncio

async def main(daily=False, **kwargs):
    try:

        if daily == True:
            await DailyController(**kwargs).daily_main('https://karir.com/search-lowongan')
        else:
            await MainController(**kwargs).main('https://karir.com/search-lowongan')

    except asyncio.CancelledError:
        await log_message('CRITICAL', 'logs/error.log', 'Task was cancelled')



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script untuk menjalankan dengan argumen.")
    parser.add_argument('--headless', action='store_true', help="Running Chromium dengan mode headless")
    parser.add_argument('--json',  action='store_true', help="Save data as json")
    parser.add_argument('--kafka', action="store_true", help="send data to kafka")
    parser.add_argument('--daily', action='store_true', help="get data by today date")
    parser.add_argument('-urutkan', type=str, choices=['terbaru', 'prioritas', 'paling populer', 'gaji tertinggi'], help="get daya by [terbaru, prioritas, paling populer, gaji tertinggi].")

    args = parser.parse_args()
    kwargs = vars(args)
    asyncio.run(main(**kwargs))