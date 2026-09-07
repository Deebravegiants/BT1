# [M] Magento Reflected Cross-site Scripting vulnerability via 'file' parameter

## Summary
Severity: Medium
Advisory: GHSA-jwxh-wj79-ccm6
CVE: CVE-2021-21029
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jwxh-wj79-ccm6
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=0 <2.3.6-p1
- Packagist: `magento/community-edition` — affected >=2.4.0 <2.4.2

## Details
Magento versions 2.4.1 (and earlier), 2.4.0-p1 (and earlier) and 2.3.6 (and earlier) are affected by a Reflected Cross-site Scripting vulnerability via 'file' parameter. Successful exploitation could lead to arbitrary JavaScript execution in the victim's browser. Access to the admin console is required for successful exploitation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21029
- https://github.com/magento/magento2/commit/a2eb7e29ea92a8bbc86c3b6b81b59d8533088497
- https://github.com/magento/magento2/commit/a349e022c9ae070e7da262021f9ef182105aa00b
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-08.html
