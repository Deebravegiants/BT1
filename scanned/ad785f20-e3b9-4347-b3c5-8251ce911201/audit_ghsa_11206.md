# [M] Statamic's missing authorization allows access to email addresses

## Summary
Severity: Medium
Advisory: GHSA-w878-f8c6-7r63
CVE: CVE-2026-28424
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-01
Source: https://github.com/advisories/GHSA-w878-f8c6-7r63
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.73.11
- Packagist: `statamic/cms` — affected >=6.0.0-alpha.1 <6.4.0

## Details
### Impact
User email addresses were included in responses from the user fieldtype’s data endpoint for control panel users who did not have the “view users” permission.

### Patches
This has been fixed in 5.73.11 and 6.4.0.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-w878-f8c6-7r63
- https://nvd.nist.gov/vuln/detail/CVE-2026-28424
- https://github.com/statamic/cms
- https://github.com/statamic/cms/releases/tag/v5.73.11
- https://github.com/statamic/cms/releases/tag/v6.4.0
