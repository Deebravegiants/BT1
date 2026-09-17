# [H] SiYuan before v3.7.3 SQL Injection via searchEmbedBlock

## Summary
Severity: High
Advisory: CVE-2026-69084
Aliases: GHSA-vh22-h7hf-www7, GO-2026-6377
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-69084
Type: osv

## Details
SiYuan versions <= v3.7.2 expose the /api/search/searchEmbedBlock endpoint, which passes a client-supplied SQL statement verbatim to the main read-write siyuan.db handle with no single-statement, read-only, or admin restrictions. The endpoint is gated only by CheckAuth, making it reachable by the publish RoleReader token and by anonymous users when publish authentication is disabled. Because the underlying driver executes stacked statements, an attacker can read and modify content across all opened cleartext notebooks (encrypted per-box notebooks are excluded). Fixed in v3.7.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69084.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-vh22-h7hf-www7
- https://nvd.nist.gov/vuln/detail/CVE-2026-69084
- https://www.vulncheck.com/advisories/siyuan-before-sql-injection-via-searchembedblock
