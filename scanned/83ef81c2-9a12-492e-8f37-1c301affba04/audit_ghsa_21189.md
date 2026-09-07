# [M] OroCommerce vulnerable to XSS when adding class name to Selector Manager on pages that use GrapeJS editor

## Summary
Severity: Medium
Advisory: GHSA-6f85-3f8q-qc94
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2022-07-15
Source: https://github.com/advisories/GHSA-6f85-3f8q-qc94
Type: github-advisory

## Affected
- Packagist: `oro/commerce` — affected >=5.0 <5.0.4

## Details
# Impact
Due to insufficient class name validation in GrapeJS library it's possible to add executable JS code in class name through Selector Manager

# Relates to
 - [https://github.com/artf/grapesjs/issues/4411](https://github.com/artf/grapesjs/issues/4411)

# Patch
Update GrapeJS dependency to >=[v0.19.5](https://github.com/artf/grapesjs/releases/tag/v0.19.5)

## References
- https://github.com/oroinc/orocommerce/security/advisories/GHSA-6f85-3f8q-qc94
- https://github.com/artf/grapesjs/issues/4411
- https://github.com/oroinc/orocommerce
