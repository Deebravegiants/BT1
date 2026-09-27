# [C] Vikunja through 2.4.0 Principal-Type Confusion via LinkSharing

## Summary
Severity: Critical
Advisory: CVE-2026-76216
Aliases: GHSA-32r8-5843-4qw2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-76216
Type: osv

## Details
Vikunja through 2.4.0 contains a principal-type confusion vulnerability where LinkSharing principals with id N are treated as user principals with users.id == N at three permission checks lacking type guards. Attackers with a link-share JWT can remove victims from teams, enumerate and delete victim bot users, or read team rosters by exploiting id collisions in the autoincrement space.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76216.json
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-32r8-5843-4qw2
- https://nvd.nist.gov/vuln/detail/CVE-2026-76216
- https://www.vulncheck.com/advisories/vikunja-through-principal-type-confusion-via-linksharing
