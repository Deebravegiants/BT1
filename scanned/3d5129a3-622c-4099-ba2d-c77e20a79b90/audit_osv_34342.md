# [C] rAthena has SQL Injection in PartyBooking component via `WorldName` parameter.

## Summary
Severity: Critical
Advisory: CVE-2025-58448
Aliases: GHSA-x99j-36m7-4vv7
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-09-09
Source: https://osv.dev/vulnerability/CVE-2025-58448
Type: osv

## Details
rAthena is an open-source cross-platform massively multiplayer online role playing game (MMORPG) server. Versions prior to commit 0d89ae0 have a SQL Injection in the PartyBooking component via `WorldName` parameter. Commit 0d89ae0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58448.json
- https://github.com/rathena/rathena/security/advisories/GHSA-x99j-36m7-4vv7
- https://nvd.nist.gov/vuln/detail/CVE-2025-58448
- https://github.com/rathena/rathena/commit/0d89ae071ff5e46e8dedcf45d060acec84b3abb5
