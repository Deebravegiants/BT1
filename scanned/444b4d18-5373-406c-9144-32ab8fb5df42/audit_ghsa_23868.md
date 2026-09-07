# [H] Magento affected by a server-side denial-of-service using a GraphQL field

## Summary
Severity: High
Advisory: GHSA-wr57-3h2f-3q95
CVE: CVE-2021-36044
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-wr57-3h2f-3q95
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected 2.4.2
- Packagist: `magento/community-edition` — affected >=2.4.2-p1 <2.4.2-p2
- Packagist: `magento/community-edition` — affected 2.3.7
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p1

## Details
Magento Commerce versions 2.4.2 (and earlier), 2.4.2-p1 (and earlier) and 2.3.7 (and earlier) are affected by an improper input validation vulnerability. An unauthenticated attacker could abuse this vulnerability to cause a server-side denial-of-service using a GraphQL field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36044
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-64.html
