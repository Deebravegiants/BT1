# [M] @backstage/plugin-techdocs-backend vulnerable to circumvention of cross site scripting protection

## Summary
Severity: Medium
Advisory: GHSA-5j94-f3mf-8685
CVE: CVE-2024-46976
CWE: CWE-693, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-5j94-f3mf-8685
Type: github-advisory

## Affected
- npm: `@backstage/plugin-techdocs-backend` — affected >=0 <1.10.13

## Details
### Impact

An attacker with control of the contents of the TechDocs storage buckets is able to inject executable scripts in the TechDocs content that will be executed in the victim's browser when browsing documentation or navigating to an attacker provided link.

### Patches

This has been fixed in the 1.10.13 release of the `@backstage/plugin-techdocs-backend` package.

### References

If you have any questions or comments about this advisory:

Open an issue in the [Backstage repository](https://github.com/backstage/backstage)
Visit our Discord, linked to in [Backstage README](https://github.com/backstage/backstage)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-5j94-f3mf-8685
- https://nvd.nist.gov/vuln/detail/CVE-2024-46976
- https://github.com/backstage/backstage
