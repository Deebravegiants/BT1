# [H] stale custom cookie host causes cookie leak

## Summary
Severity: High
Advisory: CVE-2026-6276
Aliases: CURL-CVE-2026-6276
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-6276
Type: osv

## Details
Using libcurl, when a custom `Host:` header is first set for an HTTP request
and a second request is subsequently done using the same *easy handle* but
without the custom `Host:` header set, the second request would use stale
information and pass on cookies meant for the first host in the second
request. Leak them.

## References
- http://www.openwall.com/lists/oss-security/2026/04/29/13
- https://curl.se/docs/CVE-2026-6276.html
- https://curl.se/docs/CVE-2026-6276.json
- https://hackerone.com/reports/3671818
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6276.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6276
