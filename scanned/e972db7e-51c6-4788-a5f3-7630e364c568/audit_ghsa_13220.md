# [C] Magento XML Injection vulnerability in the Widgets Update Layout

## Summary
Severity: Critical
Advisory: GHSA-8cjg-f53m-8m9q
CVE: CVE-2021-36023
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-8cjg-f53m-8m9q
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p1
- Packagist: `magento/community-edition` — affected 2.3.7
- Packagist: `magento/community-edition` — affected >=2.4.2-p1 <2.4.2-p2
- Packagist: `magento/community-edition` — affected 2.4.2

## Details
Magento Commerce versions 2.4.2 (and earlier), 2.4.2-p1 (and earlier) and 2.3.7 (and earlier) are affected by an XML Injection vulnerability in the Widgets Update Layout. An attacker with admin privileges can trigger a specially crafted script to achieve remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36023
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-64.html
