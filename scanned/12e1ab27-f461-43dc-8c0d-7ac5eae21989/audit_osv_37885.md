# [C] Chamilo LMS affected by unauthenticated RCE in main/install folder

## Summary
Severity: Critical
Advisory: CVE-2026-33698
Aliases: GHSA-557g-2w66-gpmf
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-33698
Type: osv

## Details
Chamilo LMS is a learning management system. Prior to 1.11.38, a chained attack can enable otherwise-blocked PHP code from the main/install/ directory and allow an unauthenticated attacker to modify existing files or create new files where allowed by system permissions. This only affects portals with the main/install/ directory still present and read-accessible. This vulnerability is fixed in 1.11.38.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33698.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-557g-2w66-gpmf
- https://nvd.nist.gov/vuln/detail/CVE-2026-33698
- https://github.com/chamilo/chamilo-lms/commit/d3355d7873c7e5b907c5fa84cbd5d9b62ed33e51
