# [M] Magento Open Source Cross-Site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5632-wq7m-gfq9
CVE: CVE-2024-34105
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-13
Source: https://github.com/advisories/GHSA-5632-wq7m-gfq9
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected 2.4.7
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.4
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p6
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p8
- Packagist: `magento/community-edition` — affected >=0 <2.4.4-p9

## Details
Adobe Commerce versions 2.4.7, 2.4.6-p5, 2.4.5-p7, 2.4.4-p8 and earlier are affected by a stored Cross-Site Scripting (XSS) vulnerability that could be abused by an admin attacker to inject malicious scripts into vulnerable form fields. Malicious JavaScript may be executed in a victim’s browser when they browse to the page containing the vulnerable field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34105
- https://github.com/magento/magento2/commit/30877fce83b793f71421c47347885cf076e81799
- https://github.com/magento/magento2/commit/a3c6d6e5e95e63031e4df26cfcf76feace7549c2
- https://github.com/magento/magento2/commit/c5c538810b87449886f4669cb8abbe8e5593c83c
- https://github.com/magento/magento2/commit/d10435b11ada4e502dca7539f8fd31d059d3c482
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb24-40.html
