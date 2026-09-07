# [M] Ghost's improper authentication allows access to member information and actions

## Summary
Severity: Medium
Advisory: GHSA-78x2-cwp9-5j42
CVE: CVE-2024-43409
CWE: CWE-284, CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-20
Source: https://github.com/advisories/GHSA-78x2-cwp9-5j42
Type: github-advisory

## Affected
- npm: `ghost` — affected >=4.46.0 <5.89.5
- npm: `@tryghost/portal` — affected >=1.22.2 <2.39.0

## Details
### Impact

Improper authentication on some endpoints used for member actions would allow an attacker to perform member-only actions, and read member information.

### Vulnerable versions

This security vulnerability is present in Ghost v4.46.0-v5.89.5.

Ghost(Pro) customers are automatically updated to fixed versions ahead of disclosure.

If you're a self-hoster, please follow our [update instructions](https://ghost.org/docs/update).

### Patches

v5.89.5 contains a fix for this issue.

### Workarounds

Disable site membership in Ghost settings.

### For more information

If you have any questions or comments about this advisory:

* Email us at [security@ghost.org](mailto:security@ghost.org)

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-78x2-cwp9-5j42
- https://nvd.nist.gov/vuln/detail/CVE-2024-43409
- https://github.com/TryGhost/Ghost/commit/dac25612520b571f58679764ecc27109e641d1db
- https://github.com/TryGhost/Ghost
