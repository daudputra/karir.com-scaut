from src.controller.daily import DailyController

import argparse
import asyncio

async def main(**kwargs):
    await DailyController().daily_main('https://karir.com/search-lowongan', **kwargs)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script untuk menjalankan Controller dengan argumen.")
    parser.add_argument('--headless',  action='store_true', help="Running Chromium dengan mode headless")
    asyncio.run(main())