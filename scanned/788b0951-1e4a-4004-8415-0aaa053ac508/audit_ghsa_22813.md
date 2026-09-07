# [H] Magento XML Injection vulnerability in the 'City' field

## Summary
Severity: High
Advisory: GHSA-xvpx-6hh8-7h72
CVE: CVE-2021-36020
CWE: CWE-91
Ecosystem: Packagist
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xvpx-6hh8-7h72
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p1
- Packagist: `magento/community-edition` — affected 2.3.7
- Packagist: `magento/community-edition` — affected >=2.4.2-p1 <2.4.2-p2
- Packagist: `magento/community-edition` — affected 2.4.2

## Details
Magento Commerce versions 2.4.2 (and earlier), 2.4.2-p1 (and earlier) and 2.3.7 (and earlier) are affected by an XML Injection vulnerability in the 'City' field. An unauthenticated attacker can trigger a specially crafted script to achieve remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36020
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-64.html
