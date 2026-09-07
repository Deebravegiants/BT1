# [C] Magento Blind SQL Injection in the Search module

## Summary
Severity: Critical
Advisory: GHSA-rj4f-cp4v-hvcv
CVE: CVE-2021-21024
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rj4f-cp4v-hvcv
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=0 <2.3.6-p1
- Packagist: `magento/community-edition` — affected >=2.4.0 <2.4.1-p1

## Details
Magento versions 2.4.1 (and earlier), 2.4.0-p1 (and earlier) and 2.3.6 (and earlier) are affected by a blind SQL injection vulnerability in the Search module. Successful exploitation could lead to unauthorized access to restricted resources by an unauthenticated attacker. Access to the admin console is required for successful exploitation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21024
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-08.html
