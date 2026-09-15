# [H] @backstage/plugin-techdocs-backend storage bucket Directory Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-39v3-f278-vj3g
CVE: CVE-2024-45816
CWE: CWE-22, CWE-23
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-39v3-f278-vj3g
Type: github-advisory

## Affected
- npm: `@backstage/plugin-techdocs-backend` — affected >=0 <1.10.13

## Details
### Impact

When using the AWS S3 or GCS storage provider for TechDocs it is possible to access content in the entire storage bucket. This can leak contents of the bucket that are not intended to be accessible, as well as bypass permission checks in Backstage.

### Patches

This has been fixed in the 1.10.13 release of the `@backstage/plugin-techdocs-backend` package.

### References

If you have any questions or comments about this advisory:

Open an issue in the [Backstage repository](https://github.com/backstage/backstage)
Visit our Discord, linked to in [Backstage README](https://github.com/backstage/backstage)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-39v3-f278-vj3g
- https://nvd.nist.gov/vuln/detail/CVE-2024-45816
- https://github.com/backstage/backstage
