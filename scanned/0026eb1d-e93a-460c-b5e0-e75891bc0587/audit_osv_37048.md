# [C] Group-Office Vulnerable to Remote Code Execution (RCE)

## Summary
Severity: Critical
Advisory: CVE-2026-27947
Aliases: GHSA-2rwh-9qp7-f92x
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-27947
Type: osv

## Details
Group-Office is an enterprise customer relationship management and groupware tool. Versions prior to 26.0.9, 25.0.87, and 6.8.154 have an authenticated Remote Code Execution vulnerability in the TNEF attachment processing flow. The vulnerable path extracts attacker-controlled files from `winmail.dat` and then invokes `zip` with a shell wildcard (`*`). Because extracted filenames are attacker-controlled, they can be interpreted as `zip` options and lead to arbitrary command execution. Versions 26.0.9, 25.0.87, and 6.8.154 fix the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27947.json
- https://github.com/Intermesh/groupoffice/security/advisories/GHSA-2rwh-9qp7-f92x
- https://nvd.nist.gov/vuln/detail/CVE-2026-27947
