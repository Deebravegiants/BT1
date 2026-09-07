# [M] Magento Open Source allows Incorrect Authorization

## Summary
Severity: Medium
Advisory: GHSA-f989-3fp9-q3r2
CVE: CVE-2023-29288
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-06-15
Source: https://github.com/advisories/GHSA-f989-3fp9-q3r2
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p3
- Packagist: `magento/community-edition` — affected >=2.4.4-p1 <2.4.4-p4
- Packagist: `magento/community-edition` — affected 2.4.4
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Adobe Commerce versions 2.4.6 (and earlier), 2.4.5-p2 (and earlier) and 2.4.4-p3 (and earlier) are affected by an Incorrect Authorization vulnerability that could result in a security feature bypass. A privileged attacker could leverage this vulnerability to modify a minor functionality of another user's data. Exploitation of this issue does not require user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-29288
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb23-35.html
