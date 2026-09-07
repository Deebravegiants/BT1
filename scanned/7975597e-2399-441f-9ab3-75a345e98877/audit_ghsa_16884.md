# [M] aiohttp Cross-site Scripting vulnerability on index pages for static file handling

## Summary
Severity: Medium
Advisory: GHSA-7gpw-8wmc-pm8g
CVE: CVE-2024-27306
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-04-18
Source: https://github.com/advisories/GHSA-7gpw-8wmc-pm8g
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.9.4

## Details
### Summary

A XSS vulnerability exists on index pages for static file handling.

### Details

When using `web.static(..., show_index=True)`, the resulting index pages do not escape file names.

If users can upload files with arbitrary filenames to the static directory, the server is vulnerable to XSS attacks.

### Workaround

We have always recommended using a reverse proxy server (e.g. nginx) for serving static files. Users following the recommendation are unaffected.

Other users can disable `show_index` if unable to upgrade.

-----

Patch: https://github.com/aio-libs/aiohttp/pull/8319/files

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-7gpw-8wmc-pm8g
- https://nvd.nist.gov/vuln/detail/CVE-2024-27306
- https://github.com/aio-libs/aiohttp/pull/8319
- https://github.com/aio-libs/aiohttp/pull/8319/files
- https://github.com/aio-libs/aiohttp/commit/28335525d1eac015a7e7584137678cbb6ff19397
- https://github.com/aio-libs/aiohttp
- https://lists.debian.org/debian-lts-announce/2025/02/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2EXRGTN2WG7VZLUZ7WOXU5GQJKCPPHKP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NWEI6NIHZ3G7DURDZVMRK7ZEFC2BTD3U
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZIVBMPEY7WWOFMC3CWXFBRQPFECV4SW3
