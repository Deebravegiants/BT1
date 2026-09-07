# [C] Magento OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-rv48-v862-mp92
CVE: CVE-2021-21018
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rv48-v862-mp92
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=0 <2.3.6
- Packagist: `magento/community-edition` — affected >=2.4.0 <2.4.1-p1

## Details
Magento versions 2.4.1 (and earlier), 2.4.0-p1 (and earlier) and 2.3.6 (and earlier) are vulnerable to OS command injection via the scheduled operation module. Successful exploitation could lead to arbitrary code execution by an authenticated attacker. Access to the admin console is required for successful exploitation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21018
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-08.html
