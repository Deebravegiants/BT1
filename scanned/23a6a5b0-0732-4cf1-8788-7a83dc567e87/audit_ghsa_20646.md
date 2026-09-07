# [C] Magento XML Injection vulnerability in the Widgets Module

## Summary
Severity: Critical
Advisory: GHSA-cj7w-pm77-hvg6
CVE: CVE-2022-34253
CWE: CWE-91
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-17
Source: https://github.com/advisories/GHSA-cj7w-pm77-hvg6
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p4
- Packagist: `magento/community-edition` — affected >=2.4.4 <2.4.5
- Packagist: `magento/community-edition` — affected >=2.4.0 <2.4.3-p3

## Details
Adobe Commerce versions 2.4.3-p2 (and earlier), 2.3.7-p3 (and earlier) and 2.4.4 (and earlier) are affected by an XML Injection vulnerability in the Widgets Module. An attacker with admin privileges can trigger a specially crafted script to achieve remote code execution. Exploitation of this issue does not require user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34253
- https://github.com/magento/magento2/commit/246d524b7586af2245092008e0d92b8d6fdd8523
- https://github.com/magento/magento2/commit/5548bc64b5bc904346c0af9193a7fbb5274b4efa
- https://github.com/magento/magento2/commit/5f07eba878296a37bd5c3a2baecad48948547594
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb22-38.html
