# [H] WWBN AVideo Broken Access Control via videoViewsInfo hash Parameter

## Summary
Severity: High
Advisory: CVE-2026-86190
Aliases: GHSA-82q2-88mq-p44q
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-86190
Type: osv

## Details
WWBN AVideo contains a broken access control vulnerability in videoViewsInfo endpoints that returns complete user records including password hashes, recovery tokens, and live session identifiers to unauthenticated callers when a hash parameter is provided. Attackers can use the disclosed session identifier to hijack viewer sessions, including administrator accounts, and obtain sensitive personal data for all video viewers.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86190.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-82q2-88mq-p44q
- https://nvd.nist.gov/vuln/detail/CVE-2026-86190
- https://www.vulncheck.com/advisories/wwbn-avideo-broken-access-control-via-videoviewsinfo-hash-parameter
