# [M] Magento incorrect permissions vulnerability in the Integrations component

## Summary
Severity: Medium
Advisory: GHSA-hvf5-4jr9-fghh
CVE: CVE-2020-24402
CWE: CWE-276, CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hvf5-4jr9-fghh
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=0 <2.3.6
- Packagist: `magento/community-edition` — affected >=2.4.0 <2.4.1
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Magento version 2.4.0 and 2.3.5p1 (and earlier) are affected by an incorrect permissions vulnerability in the Integrations component. This vulnerability could be abused by authenticated users with permissions to the Resource Access API to delete customer details via the REST API without authorization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24402
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb20-59.html
