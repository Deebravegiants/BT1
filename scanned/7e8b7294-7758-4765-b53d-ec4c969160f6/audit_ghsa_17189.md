# [M] Storefront user can access history and most viewed data from matching back-office user with the same ID

## Summary
Severity: Medium
Advisory: GHSA-v7px-46v9-5qwp
CVE: CVE-2023-48296
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-03-25
Source: https://github.com/advisories/GHSA-v7px-46v9-5qwp
Type: github-advisory

## Affected
- Packagist: `oro/customer-portal` — affected >=4.1.0
- Packagist: `oro/customer-portal` — affected >=4.2.0
- Packagist: `oro/customer-portal` — affected >=5.0.0
- Packagist: `oro/customer-portal` — affected >=5.1.0 <5.1.4

## Details
### Impact

Navigation history, most viewed and favorite navigation items are returned to storefront user in JSON navigation response if ID of storefront user matches ID of back-office user.

## References
- https://github.com/oroinc/orocommerce/security/advisories/GHSA-v7px-46v9-5qwp
- https://nvd.nist.gov/vuln/detail/CVE-2023-48296
- https://github.com/oroinc/orocommerce/commit/41c526498012d44cd88852c63697f1ef53b61db8
- https://github.com/oroinc/orocommerce
