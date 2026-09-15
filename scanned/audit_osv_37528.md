# [M] Tautulli: SQL Injection in get_home_stats API endpoint via unsanitised filter parameters

## Summary
Severity: Medium
Advisory: CVE-2026-31799
Aliases: GHSA-g47q-8j8w-m63q
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-31799
Type: osv

## Details
Tautulli is a Python based monitoring and tracking tool for Plex Media Server. From version 2.14.2 to before version 2.17.0 for parameters "before" and "after" and from version 2.1.0-beta to before version 2.17.0 for parameters "section_id" and "user_id", the /api/v2?cmd=get_home_stats endpoint passes the section_id, user_id, before, and after query parameters directly into SQL via Python %-string formatting without parameterization. An attacker who holds the Tautulli admin API key can inject arbitrary SQL and exfiltrate any value from the Tautulli SQLite database via boolean-blind inference. This issue has been patched in version 2.17.0.

## References
- https://github.com/Tautulli/Tautulli/releases/tag/v2.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31799.json
- https://github.com/Tautulli/Tautulli/security/advisories/GHSA-g47q-8j8w-m63q
- https://nvd.nist.gov/vuln/detail/CVE-2026-31799
