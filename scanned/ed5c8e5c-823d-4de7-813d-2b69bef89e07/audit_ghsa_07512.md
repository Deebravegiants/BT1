# [M] OpenRun: Redirect URL validation bypass using  //host  paths leads to Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-h5g6-xmh4-hc37
CVE: CVE-2026-55252
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-h5g6-xmh4-hc37
Type: github-advisory

## Affected
- Go: `github.com/openrundev/openrun` — affected >=0 <0.17.7

## Details
### Summary
The restrictions on redirect URLs in `openrun` can be bypassed by attackers, leading to open redirect attacks.

### Details

In the current project, the referrer header value is used for subsequent redirects, so there is currently a validation for this redirect value. The current validation logic requires that the host and schema of the redirect URL be the same as the current website's URL, and finally, the path part is used for redirection. This check seems robust, but it can still be bypassed by attackers.

<img width="1606" height="1346" alt="QQ20260602-140205-2-2" src="https://github.com/user-attachments/assets/83c549f3-38d7-444d-90f0-131d806f67ff" />

Here's the problem: Assuming the current website is `http://127.0.0.1:25222/`, if the attacker passes in a redirect URL of `http://127.0.0.1:25222//fushuling.com`, its host and schema are obviously the same as the current website, thus bypassing the verification. However, the issue lies in the final redirect URL, which is the path part of the URL, i.e., `//fushuling.com`. 

Browsers automatically complete the HTTP header for URLs starting with `//`, ultimately successfully bypassing the restriction and redirecting to the external address `http://fushuling.com`.

This vulnerable behavior was successfully reproduced locally. Normally, specifying an external address directly will be blocked, so it will not redirect.

<img width="1587" height="717" alt="QQ20260602-140756-2-3" src="https://github.com/user-attachments/assets/51430c42-bd10-401b-9c9f-27a91a0bc648" />

However, if the redirect URL is `http://127.0.0.1:25222//fushuling.com`, the existing validation logic is bypassed, and the Location header is successfully set to `//fushuling.com`.

```
POST /redirecttest/abc/frag HTTP/1.1
Host: 127.0.0.1:25222
Referer: http://127.0.0.1:25222//fushuling.com
Cache-Control: max-age=0
sec-ch-ua: "Not(A:Brand";v="24", "Chromium";v="122"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.57 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Connection: close
Content-Type: application/x-www-form-urlencoded
Content-Length: 0

```
<img width="1536" height="729" alt="QQ20260602-140925-2-4" src="https://github.com/user-attachments/assets/31fde919-5f90-409f-8b14-af6c9c71761b" />

The user was then successfully redirected to the external address `http://fushuling.com`.

<img width="1692" height="855" alt="QQ20260602-141005-2-5" src="https://github.com/user-attachments/assets/83b43ef6-52fa-4218-908b-7795394ae707" />

### PoC
```
http://127.0.0.1:25222//fushuling.com
```

### Impact
Open Redirect

## References
- https://github.com/openrundev/openrun/security/advisories/GHSA-h5g6-xmh4-hc37
- https://github.com/openrundev/openrun/commit/709da784fcf1311c85f30f3542cfa3601a78bbf0
- https://github.com/openrundev/openrun
- https://github.com/openrundev/openrun/releases/tag/v0.17.7
