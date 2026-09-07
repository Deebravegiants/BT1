# [M] Magento cross-site request forgery (CSRF) vulnerability via the GraphQL API

## Summary
Severity: Medium
Advisory: GHSA-h4xc-577p-hgj9
CVE: CVE-2021-21027
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h4xc-577p-hgj9
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=0 <2.3.6-p1
- Packagist: `magento/community-edition` — affected >=2.4.0 <2.4.2
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Magento versions 2.4.1 (and earlier), 2.4.0-p1 (and earlier) and 2.3.6 (and earlier) are affected by a cross-site request forgery (CSRF) vulnerability via the GraphQL API. Successful exploitation could lead to unauthorized modification of customer metadata by an unauthenticated attacker. Access to the admin console is not required for successful exploitation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21027
- https://github.com/magento/magento2/commit/a2eb7e29ea92a8bbc86c3b6b81b59d8533088497
- https://github.com/magento/magento2/commit/a349e022c9ae070e7da262021f9ef182105aa00b
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-08.html
