# [M] DataEase has a Path Traversal Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2026-45532
Aliases: GHSA-2mqc-w4hm-f3p9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-45532
Type: osv

## Details
DataEase is an open source data visualization and analysis tool. Versions prior to 2.10.23 have a path traversal vulnerability. The root cause is that on Windows, the `FILE_SEPARATOR` is `\`, while the server only filters the `/` character during string truncation. The vulnerability has been fixed in v2.10.23. No known workarounds are available.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45532.json
- https://github.com/dataease/dataease/security/advisories/GHSA-2mqc-w4hm-f3p9
- https://nvd.nist.gov/vuln/detail/CVE-2026-45532
