# [H] Magento Remote code execution through catalog attribute sets

## Summary
Severity: High
Advisory: GHSA-qpc8-m2xm-9w75
CVE: CVE-2019-8231
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qpc8-m2xm-9w75
Type: github-advisory

## Affected
- Packagist: `magento/core` — affected >=0 <1.9.4.3

## Details
In Magento Open Source prior to 1.9.4.3, and Magento Commerce prior to 1.14.4.3, an authenticated user with administrative privileges for editing attribute sets can execute arbitrary code through custom layout modification.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8231
- https://magento.com/security/patches/supee-11219
