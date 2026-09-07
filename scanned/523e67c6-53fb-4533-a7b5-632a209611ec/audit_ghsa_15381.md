# [H] Magento Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-7r99-8wqp-h7pc
CVE: CVE-2024-39399
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-08-14
Source: https://github.com/advisories/GHSA-7r99-8wqp-h7pc
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1 <2.4.7-p2
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p7
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p9
- Packagist: `magento/community-edition` — affected >=2.4.4-p1 <2.4.4-p10
- Packagist: `magento/community-edition` — affected 2.4.7
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.4

## Details
Magento versions 2.4.7-p1, 2.4.6-p6, 2.4.5-p8, 2.4.4-p9 and earlier are affected by an Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal') vulnerability that could lead to arbitrary file system read. A low-privileged attacker could exploit this vulnerability to gain access to files and directories that are outside the restricted directory. Exploitation of this issue does not require user interaction and scope is changed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39399
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb24-61.html
