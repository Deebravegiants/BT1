# [M] ClearanceKit has a policy bypass via dual-path Endpoint Security events checking only source path

## Summary
Severity: Medium
Advisory: CVE-2026-40191
Aliases: GHSA-92f3-38m7-579h
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-40191
Type: osv

## Details
ClearanceKit intercepts file-system access events on macOS and enforces per-process access policies. Prior to 5.0.4-beta-1f46165,  ClearanceKit's Endpoint Security event handler only checked the source path of dual-path file operations against File Access Authorization (FAA) rules and App Jail policies. The destination path was ignored entirely. This allowed any local process to bypass file-access protection by using rename, link, copyfile, exchangedata, or clone operations to place or replace files inside protected directories. This vulnerability is fixed in 5.0.4-beta-1f46165.

## References
- https://github.com/craigjbass/clearancekit/releases/tag/v5.0.4-1f46165
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40191.json
- https://github.com/craigjbass/clearancekit/security/advisories/GHSA-92f3-38m7-579h
- https://nvd.nist.gov/vuln/detail/CVE-2026-40191
