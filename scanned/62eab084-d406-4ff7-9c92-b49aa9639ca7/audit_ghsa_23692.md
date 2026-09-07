# [M] Magento incorrect permissions vulnerability in the Inventory module

## Summary
Severity: Medium
Advisory: GHSA-p7m7-j8jv-393q
CVE: CVE-2020-24405
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p7m7-j8jv-393q
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=0 <2.3.6
- Packagist: `magento/community-edition` — affected >=2.4.0 <2.4.1

## Details
Magento version 2.4.0 and 2.3.5p1 (and earlier) are affected by an incorrect permissions issue vulnerability in the Inventory module. This vulnerability could be abused by authenticated users to modify inventory stock data without authorization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24405
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb20-59.html
