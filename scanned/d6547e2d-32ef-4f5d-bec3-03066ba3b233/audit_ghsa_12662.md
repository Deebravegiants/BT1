# [H] Magento Open Source allows Improper Neutralization of Special Elements Used

## Summary
Severity: High
Advisory: GHSA-gfmm-ww6f-5mm5
CVE: CVE-2023-29297
CWE: CWE-1336
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-15
Source: https://github.com/advisories/GHSA-gfmm-ww6f-5mm5
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.4
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p3
- Packagist: `magento/community-edition` — affected >=2.4.4-p1 <2.4.4-p4
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Adobe Commerce versions 2.4.6 (and earlier), 2.4.5-p2 (and earlier) and 2.4.4-p3 (and earlier) are affected by a Improper Neutralization of Special Elements Used in a Template Engine vulnerability that could lead to arbitrary code execution by an admin-privilege authenticated attacker. Exploitation of this issue does not require user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-29297
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb23-35.html
