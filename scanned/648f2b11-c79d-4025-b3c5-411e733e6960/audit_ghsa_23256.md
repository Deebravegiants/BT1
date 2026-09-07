# [M] Magento observable timing discrepancy vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xgp9-j48h-jjf9
CVE: CVE-2020-9690
CWE: CWE-203
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xgp9-j48h-jjf9
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=0 <2.3.5-p2

## Details
Magento versions 2.3.5-p1 and earlier, and 2.3.5-p1 and earlier have an observable timing discrepancy vulnerability. Successful exploitation could lead to signature verification bypass.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9690
- https://github.com/magento/magento2/commit/9436781734e47c83e96977fa770d255217680d5e
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb20-47.html
