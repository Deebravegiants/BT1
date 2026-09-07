# [H] Magento affected by a blind SSRF vulnerability in the bundled dotmailer extension

## Summary
Severity: High
Advisory: GHSA-36xq-7w8w-xp68
CVE: CVE-2021-36043
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-36xq-7w8w-xp68
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p1
- Packagist: `magento/community-edition` — affected 2.3.7
- Packagist: `magento/community-edition` — affected >=2.4.2-p1 <2.4.2-p2
- Packagist: `magento/community-edition` — affected 2.4.2

## Details
Magento Commerce versions 2.4.2 (and earlier), 2.4.2-p1 (and earlier) and 2.3.7 (and earlier) are affected by a blind SSRF vulnerability in the bundled dotmailer extension. An attacker with admin privileges could abuse this to achieve remote code execution should Redis be enabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36043
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-64.html
