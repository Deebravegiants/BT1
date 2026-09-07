# [H] Magento Open Source allows Stored Cross-Site Scripting (Stored XSS)

## Summary
Severity: High
Advisory: GHSA-4vj2-426r-jm3g
CVE: CVE-2022-35698
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-15
Source: https://github.com/advisories/GHSA-4vj2-426r-jm3g
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected 2.4.4-p1
- Packagist: `magento/community-edition` — affected 2.4.4
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected >=2.4.3-p1
- Packagist: `magento/community-edition` — affected 2.4.3
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Adobe Commerce versions 2.4.3-p3 (and earlier), 2.4.4-p1 (and earlier) and 2.4.5 (and earlier) are affected by a Stored Cross-site Scripting vulnerability. Exploitation of this issue does not require user interaction and could result in a post-authentication arbitrary code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35698
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb22-48.html
