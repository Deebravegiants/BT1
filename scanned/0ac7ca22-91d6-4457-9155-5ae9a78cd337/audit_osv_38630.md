# [H] RT: SQL injection via entry_aggregator parameter in JSON search

## Summary
Severity: High
Advisory: CVE-2026-41075
Aliases: GHSA-7vf8-xv7w-97c6
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-22
Source: https://osv.dev/vulnerability/CVE-2026-41075
Type: osv

## Details
RT is an open source, enterprise-grade issue and ticket tracking system. Versions 5.0.0 through 5.0.9 and 6.0.0 through 6.0.2 contain an SQL injection vulnerability. An authenticated user can craft input that is incorporated into database queries without proper validation, potentially allowing them to read or modify data in the RT database. This issue has been fixed in versions 5.0.10 and 6.0.3. If developers are unable to upgrade immediately, they can temporarily work around this issue by restricting RT account access to trusted users.

## References
- https://github.com/bestpractical/rt/releases/tag/rt-5.0.10
- https://github.com/bestpractical/rt/releases/tag/rt-6.0.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41075.json
- https://github.com/bestpractical/rt/security/advisories/GHSA-7vf8-xv7w-97c6
- https://nvd.nist.gov/vuln/detail/CVE-2026-41075
