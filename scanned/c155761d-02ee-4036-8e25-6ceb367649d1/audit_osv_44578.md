# [M] wrong reuse for different services

## Summary
Severity: Medium
Advisory: CVE-2026-8458
Aliases: CURL-CVE-2026-8458
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-8458
Type: osv

## Details
libcurl might in some circumstances reuse the wrong connection when asked to
do Negotiate-authenticated ones, even when they are set to use different
'services'.

libcurl features a pool of recent connections so that subsequent requests can
reuse an existing connection to avoid overhead.

When reusing a connection a range of criteria must be met. Due to a logical
error in the code, a request that was issued by an application could
wrongfully reuse an existing connection to the same server that was
authenticated using different services.

## References
- https://curl.se/docs/CVE-2026-8458.html
- https://curl.se/docs/CVE-2026-8458.json
- https://hackerone.com/reports/3721183
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8458.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8458
