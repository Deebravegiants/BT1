# [M] Magento stored cross-site scripting vulnerability in the customer address upload feature

## Summary
Severity: Medium
Advisory: GHSA-8gfq-m4cf-w975
CVE: CVE-2021-36026
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8gfq-m4cf-w975
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p1
- Packagist: `magento/community-edition` — affected 2.3.7
- Packagist: `magento/community-edition` — affected >=2.4.2-p1 <2.4.2-p2
- Packagist: `magento/community-edition` — affected 2.4.2

## Details
Magento Commerce versions 2.4.2 (and earlier), 2.4.2-p1 (and earlier) and 2.3.7 (and earlier) are affected by a stored cross-site scripting vulnerability in the customer address upload feature that could be abused by an attacker to inject malicious scripts into vulnerable form fields. Malicious JavaScript may be executed in a victim’s browser when they browse to the page containing the vulnerable field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36026
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-64.html
