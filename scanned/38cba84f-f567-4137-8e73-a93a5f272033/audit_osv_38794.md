# [C] Emlog: SQL Injection Vulnerability in log_model.php within addLog() and updateLog() Functions

## Summary
Severity: Critical
Advisory: CVE-2026-42287
Aliases: GHSA-xxj8-fc63-j3gw
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42287
Type: osv

## Details
Emlog is an open source website building system. Prior to version 2.6.11, direct SQL injection in article creation and update functions allows attackers to execute arbitrary SQL commands, potentially leading to complete database compromise, data theft, or system destruction. This issue has been patched in version 2.6.11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42287.json
- https://github.com/emlog/emlog/security/advisories/GHSA-xxj8-fc63-j3gw
- https://nvd.nist.gov/vuln/detail/CVE-2026-42287
