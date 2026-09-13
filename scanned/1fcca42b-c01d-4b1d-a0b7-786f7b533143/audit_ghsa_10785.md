# [H] Statamic: Unsafe method invocation via query value resolution allows data destruction

## Summary
Severity: High
Advisory: GHSA-4jjr-vmv7-wh4w
CVE: CVE-2026-41175
CWE: CWE-470
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-4jjr-vmv7-wh4w
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.73.20
- Packagist: `statamic/cms` — affected >=6.0.0-alpha.1 <6.13.0

## Details
### Impact

Manipulating query parameters on Control Panel and REST API endpoints, or arguments in GraphQL queries, could result in the loss of content, assets, and user accounts.

The Control Panel requires authentication with minimal permissions in order to exploit. e.g. "view entries" permission to delete entries, or "view users" permission to delete users, etc.

The REST and GraphQL API exploits do not require any permissions, however neither are enabled by default. In order to be exploited, they would need to be explicitly enabled with no authentication configured, and the specific resources enabled too.

Sites that enable the REST or GraphQL API without authentication should treat patching as critical priority.

### Patches

This has been fixed in 5.73.20 and 6.13.0.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-4jjr-vmv7-wh4w
- https://nvd.nist.gov/vuln/detail/CVE-2026-41175
- https://github.com/statamic/cms
