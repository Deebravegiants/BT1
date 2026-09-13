# [M] Statamic: Missing authorization on Control Panel endpoint allows disclosure of user existence

## Summary
Severity: Medium
Advisory: GHSA-225x-3jhx-wh4q
CVE: CVE-2026-64664
CWE: CWE-200, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-225x-3jhx-wh4q
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.74.1
- Packagist: `statamic/cms` — affected >=6.0.0 <6.24.0

## Details
### Impact
An authenticated Control Panel user could use an endpoint intended for the user creation wizard to determine if a given email address belongs to an existing user, without having permission to view users.

The endpoint only exposed user existence, not any of its data.

### Patches
This has been fixed in 5.74.1 and 6.24.0.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-225x-3jhx-wh4q
- https://github.com/statamic/cms/pull/14905
- https://github.com/statamic/cms/commit/aea68053cedab5c79d10102820b57345a7d7102e
- https://github.com/statamic/cms
- https://github.com/statamic/cms/releases/tag/v5.74.1
- https://github.com/statamic/cms/releases/tag/v6.24.0
