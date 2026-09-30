# [M] TeamPass does not properly check whether a folder is in a user's allowed folders list

## Summary
Severity: Medium
Advisory: GHSA-2697-96mv-3gfm
CVE: CVE-2024-50701
CWE: CWE-266, CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-12-30
Source: https://github.com/advisories/GHSA-2697-96mv-3gfm
Type: github-advisory

## Affected
- Packagist: `nilsteampassnet/teampass` — affected >=0 <3.1.3.1

## Details
TeamPass before 3.1.3.1, when retrieving information about access rights for a folder, does not properly check whether a folder is in a user's allowed folders list that has been defined by an admin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-50701
- https://github.com/nilsteampassnet/TeamPass/commit/ddbb2d3d94085dced50c4936fd2215af88e4a88d
- https://github.com/nilsteampassnet/TeamPass
- https://github.com/nilsteampassnet/TeamPass/compare/3.1.2...3.1.3.1
- https://github.com/nilsteampassnet/TeamPass/compare/3.1.3...3.1.3.1
