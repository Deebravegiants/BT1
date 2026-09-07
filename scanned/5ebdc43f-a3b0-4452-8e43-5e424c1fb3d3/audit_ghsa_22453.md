# [C] Magento command injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-4f7x-gjqc-qqpg
CVE: CVE-2020-9576
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4f7x-gjqc-qqpg
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.4-p2
- Packagist: `magento/community-edition` — affected >=0 <2.2.12
- Packagist: `magento/core` — affected >=0 <1.9.4.5
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Magento versions 2.3.4 and earlier, 2.2.11 and earlier (see note), 1.14.4.4 and earlier, and 1.9.4.4 and earlier have a command injection vulnerability. Successful exploitation could lead to arbitrary code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9576
- https://github.com/magento/magento2/commit/52d92dbd07f09620d23693ba0c4d4bdb4ba09916
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb20-22.html
