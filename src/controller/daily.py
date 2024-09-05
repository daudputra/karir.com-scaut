import asyncio

from src.helper.save_json import SaveJson
from src.helper.mylog import log_message

from playwright.async_api import async_playwright
from scrapy import Selector


class DailyController:

    def __init__(self, headless=True) -> None:
        self.headless = headless
        self.topic = "data-knowledge-repo-general_2"

    async def daily_main(self, url):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                context = await browser.new_context()
                # context = await browser.new_context(storage_state='state.json')
                page = await context.new_page()

                await page.goto(url, timeout=1800000)
                await page.wait_for_selector('#job-header-wrapper')
                await self._urutkan(page)
                await asyncio.sleep(4)

                index = 1
                while True:
                    await page.locator(f'text="{index}"').click()  
                    await asyncio.sleep(4)

                    html_content = await page.content()
                    await self._click_container(page, html_content)
                    index += 1

        except Exception as e:
            await log_message('ERROR', 'logs/error.py', f'error in daily_main: {e}')
        except KeyboardInterrupt:
            await log_message('CRITICAL', 'logs/error.py', f'Process interupted by keyboard')
        finally:
            await log_message('INFO', 'logs/info.log', 'Process complete, engine stopped')
            await browser.close()


    async def _urutkan(self, page):
        await page.locator('[data-testid="KeyboardArrowDownIcon"]').nth(4).click()
        await page.locator('text="Terbaru"').click()
        await asyncio.sleep(5)



    async def _click_container(self, page, html_content):
        sel = Selector(text=html_content)

        index = 2
        div_container = sel.xpath('/html/body/div/div[2]/div[3]/div/div/div/div[1]/div[position() != 1 and position() != last()]')
        for div in div_container:
            job = div.xpath('div[1]/div[2]/p[1]/text()').get().replace('\t', '')
            nama_perusahaan = div.xpath('div[1]/div[2]/p[2]/text()').get()
            gaji = div.xpath('div[1]/div[2]/p[3]/text()').get()
            provinsi = div.xpath('div[1]/div[2]/p[4]/text()').get()
            post_date = div.xpath('div[3]/div[2]/p/text()').get()


            await page.locator(f'//html/body/div/div[2]/div[3]/div/div/div/div[1]/div[{index}]').click()
            await asyncio.sleep(5) 


            html_content = await page.content()
            await self._get_detail_jobs(page, html_content, job, nama_perusahaan, gaji, provinsi, post_date)
            index += 1



    async def _get_detail_company(self, page, nama_perusahaan):
        url = f"https://karir.com/search-lowongan?keyword={nama_perusahaan}"
        new_page = await page.context.new_page()
        await new_page.goto(url, timeout=1800000)
        await asyncio.sleep(5)


        await new_page.locator('//html/body/div/div[2]/div[2]/div/div/div/div/button[2]').click()
        await asyncio.sleep(5) 

        
        html_content = await new_page.content()
        sel = Selector(text=html_content)
        informasi_perusahaan = {
            'website_perusahaan' : sel.xpath('/html/body/div[1]/div[2]/div[4]/div/div/div/div[2]/div[1]/div[1]/div/div[1]/div[2]/p[3]/text()').get(),
            'informasi_perusahaan' : {
                'Industri' : sel.xpath('/html/body/div[1]/div[2]/div[4]/div/div/div/div[2]/div[2]/div/div/div[1]/div[1]/div[1]/p[2]/text()').get(),
                'Hari Kerja' : ' '.join(sel.xpath('/html/body/div[1]/div[2]/div[4]/div/div/div/div[2]/div[2]/div/div/div[1]/div[1]/div[1]/p[4]//text()').getall()),
                'Jumlah Karyawan' : sel.xpath('/html/body/div[1]/div[2]/div[4]/div/div/div/div[2]/div[2]/div/div/div[1]/div[1]/div[2]/p[2]/text()').get(),
                'Jam Kerja' : ' '.join(sel.xpath('/html/body/div[1]/div[2]/div[4]/div/div/div/div[2]/div[2]/div/div/div[1]/div[1]/div[2]/p[4]/text()').getall()),
                'Dress Code' : sel.xpath('/html/body/div[1]/div[2]/div[4]/div/div/div/div[2]/div[2]/div/div/div[1]/div[1]/div[3]/p[2]/text()').get()
            },
            'tentang_perusahaan' : (sel.xpath('/html/body/div[1]/div[2]/div[4]/div/div/div/div[2]/div[2]/div/div/div[2]/p[2]/text()').get() or '').replace('\r','').replace('\n',''),
            'lokasi' : {
                'Kota' : (sel.xpath('/html/body/div[1]/div[2]/div[4]/div/div/div/div[2]/div[2]/div/div/div[2]/div[1]/div[1]/div/text()').get() or '').replace('\r','').replace('\n',''),
                'Alamat' : (sel.xpath('/html/body/div[1]/div[2]/div[4]/div/div/div/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div/text()').get() or '').replace('\r','').replace('\n','')
            },
            'visi_misi' : [text.strip().replace('\xa0', '').replace('\t', '').replace('\n', '') if text.strip() else '' for text in sel.xpath('/html/body/div[1]/div[2]/div[4]/div/div/div/div[2]/div[2]/div/div/div[3]/div/p//text()').getall()]
        }
        await new_page.close()
        return informasi_perusahaan



    async def _get_detail_jobs(self, page, html_content, job, nama_perusahaan, gaji, provinsi, post_date):
        try:
            sel = Selector(text=html_content)

            dilihat_sebanyak = sel.xpath('/html/body/div[1]/div[2]/div[3]/div/div/div/div[2]/div[4]/div[1]/div[2]/div[4]/div[1]/div[2]/p/text()').get()
            deskripsi = sel.xpath('/html/body/div[1]/div[2]/div[3]/div/div/div/div[2]/div[4]/div[1]/div[2]/div[4]/div[1]/div[3]/p/text()').get()
            range_data = post_date.split(' ')[-1]
            informasi_perusahaan = await self._get_detail_company(page, nama_perusahaan)
            tag = ['https://karir.com', 'Lowongan', provinsi]


            data = {
                'job' : job,
                'nama_perusahaan' : nama_perusahaan,
                'gaji' : gaji.replace('\xa0', ''),
                'provinsi': provinsi,
                'post_date' : post_date,
                'dilihat_sebanyak' : dilihat_sebanyak,
                'update' : deskripsi,
                'informasi_lowongan' : {
                    'Tipe Pekerjaan' : sel.xpath('/html/body/div/div[2]/div[3]/div/div/div/div[2]/div[5]/div/div[1]/div/div[1]/p[2]/text()').get(),
                    'Remote/On-site' : sel.xpath('/html/body/div/div[2]/div[3]/div/div/div/div[2]/div[5]/div/div[1]/div/div[1]/p[4]/text()').get(),
                    'Fungsi Pekerjaan' : sel.xpath('/html/body/div/div[2]/div[3]/div/div/div/div[2]/div[5]/div/div[1]/div/div[2]/p[2]/text()').get(),
                    'Jenjang Karir' : sel.xpath('/html/body/div/div[2]/div[3]/div/div/div/div[2]/div[5]/div/div[1]/div/div[3]/p[2]/text()').get(),
                    'Job Deskripsi' : [text.strip().replace('\xa0', '').replace('\t', '').replace('\n', '')  for text in sel.xpath('//*[@id="menu-0"]/p[position()>3]//text() | //*[@id="menu-0"]/ul//text()').getall() if text.strip()]
                },
                'persyaratan': {
                    'Tingkat Pendidikan' : sel.xpath('/html/body/div/div[2]/div[3]/div/div/div/div[2]/div[5]/div/div[2]/div/div[1]/p[2]/text()').get(),
                    'Jurusan Pendidikan' : sel.xpath('/html/body/div/div[2]/div[3]/div/div/div/div[2]/div[5]/div/div[2]/div/div[2]/p[2]/text()').get(),
                    'Minimal Pengalaman' : sel.xpath('/html/body/div/div[2]/div[3]/div/div/div/div[2]/div[5]/div/div[2]/div/div[3]/p[2]/text()').get(),
                    'Deskripsi Persyaratan' : [ text.strip().replace('\xa0', '').replace('\t', '').replace('\n', '')  for text in sel.xpath('//*[@id="menu-1"]/p[position()>3]//text() | //*[@id="menu-1"]/ul//text()').getall() if text.strip()],
                },
                'skill_yang_dibutuhkan' : sel.xpath('/html/body/div/div[2]/div[3]/div/div/div/div[2]/div[5]/div/div[3]/div//text()').getall(),
                'lokasi' : {
                    'Kota' : (sel.xpath('/html/body/div/div[2]/div[3]/div/div/div/div[2]/div[5]/div/div[4]/div/div[1]/p[2]/text()').get() or '').replace('\r','').replace('\n',''),
                    'Alamat' : (sel.xpath('/html/body/div/div[2]/div[3]/div/div/div/div[2]/div[5]/div/div[4]/div/div[2]/p[2]/text()').get() or '').replace('\r','').replace('\n','')
                },
                'detail_perusahaan' : informasi_perusahaan
            }


            filename = f"{job.replace(' ','_').lower()}_{nama_perusahaan.replace(' ','_').lower()}.json".replace('\\','').replace('/','')

            try:
                save_json = SaveJson('https://karir.com/search-lowongan', job, nama_perusahaan, range_data, post_date, tag, data)
                await save_json.save_json_local(filename, provinsi.replace(' ','_').replace('.','').lower())
                # await log_message('DEBUG', 'logs/debug.log', f"save {filename}")
            except Exception as e:
                await log_message('ERROR', 'logs/error.py', f'error in _get_detail_jobs: {e}')
        except Exception as e:
            await log_message('CRITICAL', 'logs/error.py', f'error in _get_detail_jobs: {e}')