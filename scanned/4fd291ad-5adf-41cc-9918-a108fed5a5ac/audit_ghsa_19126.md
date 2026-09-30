# [H] Adobe Commerce Path Traversal

## Summary
Severity: High
Advisory: GHSA-954p-ff72-327w
CVE: CVE-2025-24406
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-02-11
Source: https://github.com/advisories/GHSA-954p-ff72-327w
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1 <2.4.7-p4
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p9
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p11
- Packagist: `magento/community-edition` — affected >=0 <2.4.4-p12
- Packagist: `magento/community-edition` — affected 2.4.7
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.4
- Packagist: `magento/community-edition` — affected 2.4.8-beta1
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Adobe Commerce versions 2.4.8-beta1, 2.4.7-p3, 2.4.6-p8, 2.4.5-p10, 2.4.4-p11 and earlier are affected by an Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal') vulnerability that could lead to a security feature bypass. An unauthenticated attacker could exploit this vulnerability to modify files that are stored outside the restricted directory. Exploitation of this issue does not require user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24406
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb25-08.html
