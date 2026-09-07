# [C] Magento security bypass vulnerability

## Summary
Severity: Critical
Advisory: GHSA-x9p7-vgp2-9pq2
CVE: CVE-2020-3718
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x9p7-vgp2-9pq2
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.4
- Packagist: `magento/community-edition` — affected >=0 <2.2.11
- Packagist: `magneto/core` — affected >=0 <1.9.4.4

## Details
Magento versions 2.3.3 and earlier, 2.2.10 and earlier, 1.14.4.3 and earlier, and 1.9.4.3 and earlier have a security bypass vulnerability. Successful exploitation could lead to arbitrary code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-3718
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb20-02.html
