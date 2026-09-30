# [M] Permission policy information leakage in Backstage permission system

## Summary
Severity: Medium
Advisory: GHSA-f8j4-p5cr-p777
CVE: CVE-2025-32791
CWE: CWE-213
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-04-16
Source: https://github.com/advisories/GHSA-f8j4-p5cr-p777
Type: github-advisory

## Affected
- npm: `@backstage/plugin-permission-backend` — affected >=0 <0.6.0

## Details
### Impact

A vulnerability in the Backstage permission plugin backend allows callers to extract some information about the conditional decisions returned by the permission policy installed in the permission backend. If the permission system is not in use or if the installed permission policy does not use conditional decisions, there is no impact.

### Patches

This issue has been resolved in version `0.6.0` of the permissions backend.

### Workarounds

Administrators of the permission policies can ensure that they are crafted in such a way that conditional decisions do not contain any sensitive information.

### References

If you have any questions or comments about this advisory:

Open an issue in the [Backstage repository](https://github.com/backstage/backstage)
Visit our Discord, linked to in [Backstage README](https://github.com/backstage/backstage)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-f8j4-p5cr-p777
- https://nvd.nist.gov/vuln/detail/CVE-2025-32791
- https://github.com/backstage/backstage
