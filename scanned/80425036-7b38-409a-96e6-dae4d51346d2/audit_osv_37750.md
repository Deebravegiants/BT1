# [C] WeGIA has an arbitrary SQL execution vulnerability via crafted backup archive

## Summary
Severity: Critical
Advisory: CVE-2026-33133
Aliases: GHSA-qqff-p8fc-hg5f
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33133
Type: osv

## Details
WeGIA is a web manager for charitable institutions. In versions 3.6.5 and 3.6.6, the loadBackupDB() function imports SQL files from uploaded backup archives without any content validation. An attacker can craft a backup archive containing arbitrary SQL statements that create rogue administrator accounts, modify existing passwords, or execute any database operation. This was introduced in commit 370104c. This issue was patched in version 3.6.7.

## References
- https://github.com/LabRedesCefetRJ/WeGIA/releases/tag/3.6.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33133.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-qqff-p8fc-hg5f
- https://nvd.nist.gov/vuln/detail/CVE-2026-33133
- https://github.com/LabRedesCefetRJ/WeGIA/pull/1459
