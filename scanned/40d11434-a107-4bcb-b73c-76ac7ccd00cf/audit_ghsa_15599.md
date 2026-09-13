# [H] @backstage/plugin-catalog-backend Prototype Pollution vulnerability

## Summary
Severity: High
Advisory: GHSA-3x3f-jcp3-g22j
CVE: CVE-2024-45815
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-3x3f-jcp3-g22j
Type: github-advisory

## Affected
- npm: `@backstage/plugin-catalog-backend` — affected >=0 <1.26.0

## Details
### Impact

A malicious actor with authenticated access to a Backstage instance with the catalog backend plugin installed is able to interrupt the service using a specially crafted query to the catalog API.

### Patches

This has been fixed in the `1.26.0` release of the `@backstage/plugin-catalog-backend` package.

### References

If you have any questions or comments about this advisory:

Open an issue in the [Backstage repository](https://github.com/backstage/backstage)
Visit our Discord, linked to in [Backstage README](https://github.com/backstage/backstage)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-3x3f-jcp3-g22j
- https://nvd.nist.gov/vuln/detail/CVE-2024-45815
- https://github.com/backstage/backstage
