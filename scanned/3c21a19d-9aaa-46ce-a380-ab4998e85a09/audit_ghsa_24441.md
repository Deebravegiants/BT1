# [M] Magento stored cross-site scripting vulnerability in the admin console

## Summary
Severity: Medium
Advisory: GHSA-h5rm-m772-6qcx
CVE: CVE-2021-21023
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h5rm-m772-6qcx
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=0 <2.3.6
- Packagist: `magento/community-edition` — affected >=2.4.0 <2.4.1-p1
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Magento versions 2.4.1 (and earlier), 2.4.0-p1 (and earlier) and 2.3.6 (and earlier) are vulnerable to a stored cross-site scripting vulnerability in the admin console. Successful exploitation could lead to arbitrary JavaScript execution in the victim's browser. Access to the admin console is required for successful exploitation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21023
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-08.html
