# [M] Statamic is missing authorization check on taxonomy term creation via fieldtype

## Summary
Severity: Medium
Advisory: GHSA-wh3h-gvc4-cc2g
CVE: CVE-2026-33177
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-wh3h-gvc4-cc2g
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=6.0.0-alpha.1 <6.7.0
- Packagist: `statamic/cms` — affected >=0 <5.73.14

## Details
### Impact

Low-privileged Control Panel users could create taxonomy terms by submitting requests to the field action processing endpoint with attacker-controlled field definitions. This bypasses the authorization checks enforced on the standard taxonomy term creation endpoint.

### Patches

This has been fixed in 5.73.14 and 6.7.0.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-wh3h-gvc4-cc2g
- https://nvd.nist.gov/vuln/detail/CVE-2026-33177
- https://github.com/statamic/cms
