# [H] Cacti: Stored SQL Injection via graph_name_regexp in Reports feature

## Summary
Severity: High
Advisory: CVE-2026-39951
Aliases: GHSA-pf37-v86f-5xwp
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-39951
Type: osv

## Details
Cacti is an open source performance and fault management framework. Versions 1.2.30 and prior have a Stored SQL Injection vulnerability through graph_name_regexp in the Reports feature. This issue has been fixed in version 1.2.31.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39951.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-pf37-v86f-5xwp
- https://nvd.nist.gov/vuln/detail/CVE-2026-39951
- https://github.com/Cacti/cacti/commit/4c09efaebf3a9faec66969d0b5c4aceaf397f37f
