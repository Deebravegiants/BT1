# [M] ALPINE-CVE-2026-6253

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-6253
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-6253
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.14.1 <8.20.0-r0
- Alpine:v3.24: `curl` — affected >=7.14.1 <8.20.0-r0

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
- https://security.alpinelinux.org/vuln/CVE-2026-6253
