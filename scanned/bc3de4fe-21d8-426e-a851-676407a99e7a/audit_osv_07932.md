# [M] proxy credentials leak over redirect-to proxy

## Summary
Severity: Medium
Advisory: CURL-CVE-2026-6253
Aliases: CVE-2026-6253
Published: 2026-04-29
Source: https://osv.dev/vulnerability/CURL-CVE-2026-6253
Type: osv

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
