# [M] JLSEC-2026-1206

## Summary
Severity: Medium
Advisory: JLSEC-2026-1206
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1206
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.20.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.20.0+0

## Details
curl might erroneously pass on credentials for a first proxy to a second
proxy.

This can happen when the following conditions are true:

 1. curl is setup to use specific different proxies for different URL schemes
 2. the first proxy needs credentials
 3. the second proxy uses no credentials
 4. while using the first proxy (using say `http://`), curl is asked to follow
    a redirect to a URL using another scheme (say `https://`), accessed using a
    second, different, proxy

## References
- http://www.openwall.com/lists/oss-security/2026/04/29/11
- https://curl.se/docs/CVE-2026-6253.html
- https://curl.se/docs/CVE-2026-6253.json
- https://hackerone.com/reports/3669637
