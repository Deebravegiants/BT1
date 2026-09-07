# [H] Magento Signature verification bypass

## Summary
Severity: High
Advisory: GHSA-j2r4-2cr6-h3r3
CVE: CVE-2020-9588
CWE: CWE-203
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-j2r4-2cr6-h3r3
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=0 <2.3.4-p2
- Packagist: `magento/core` — affected >=0 <1.9.4.5
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Magento versions 2.3.4 and earlier, 2.2.11 and earlier (see note), 1.14.4.4 and earlier, and 1.9.4.4 and earlier have an observable timing discrepancy vulnerability. Successful exploitation could lead to signature verification bypass.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9588
- https://helpx.adobe.com/security/products/magento/apsb20-22.html
