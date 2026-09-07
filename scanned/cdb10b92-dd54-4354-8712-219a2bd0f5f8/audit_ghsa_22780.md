# [H] Magento allows attackers to alter the price of items

## Summary
Severity: High
Advisory: GHSA-rhff-65hp-55rw
CVE: CVE-2021-36030
CWE: CWE-20
Ecosystem: Packagist
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rhff-65hp-55rw
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p1
- Packagist: `magento/community-edition` — affected 2.3.7
- Packagist: `magento/community-edition` — affected >=2.4.2-p1 <2.4.2-p2
- Packagist: `magento/community-edition` — affected 2.4.2

## Details
Magento Commerce versions 2.4.2 (and earlier), 2.4.2-p1 (and earlier) and 2.3.7 (and earlier) are affected by an improper input validation vulnerability during the checkout process. An unauthenticated attacker can leverage this vulnerability to alter the price of items.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36030
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-64.html
