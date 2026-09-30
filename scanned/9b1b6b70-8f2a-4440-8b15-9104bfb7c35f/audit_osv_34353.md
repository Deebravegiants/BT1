# [H] rAthena missing bound check in chclif_parse_moveCharSlot

## Summary
Severity: High
Advisory: CVE-2025-58750
Aliases: GHSA-pjh7-jgr8-4ff6
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-09-09
Source: https://osv.dev/vulnerability/CVE-2025-58750
Type: osv

## Details
rAthena is an open-source cross-platform massively multiplayer online role playing game (MMORPG) server. Versions prior to commit 0cc348b are missing a bound check in `chclif_parse_moveCharSlot` that can result in reading and writing out of bounds using input from the user. The problem has been fixed in commit 0cc348b.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58750.json
- https://github.com/rathena/rathena/security/advisories/GHSA-pjh7-jgr8-4ff6
- https://nvd.nist.gov/vuln/detail/CVE-2025-58750
- https://github.com/rathena/rathena/commit/0cc348b186bbcc3c604c17c39589a319f27d469b
