# [H] ClipBucket v5 has time-based Blind SQL Injection in ajax.php that leads to Data Exfiltration

## Summary
Severity: High
Advisory: CVE-2026-32321
Aliases: GHSA-2757-6cp4-v7xx
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-32321
Type: osv

## Details
ClipBucket v5 is an open source video sharing platform. An authenticated time-based blind SQL injection vulnerability exists in ClipBucket prior to 5.5.3 #80 within the `actions/ajax.php` endpoint. Due to insufficient input sanitization of the `userid` parameter, an authenticated attacker can execute arbitrary SQL queries, leading to full database disclosure and potential administrative account takeover. Version 5.5.3 #80 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32321.json
- https://github.com/MacWarrior/clipbucket-v5/security/advisories/GHSA-2757-6cp4-v7xx
- https://nvd.nist.gov/vuln/detail/CVE-2026-32321
- https://github.com/MacWarrior/clipbucket-v5/commit/726d68b0c9d4c702dce2691c2759b6bf84a1691f
