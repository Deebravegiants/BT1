# [H] Magento Violation of Secure Design Principles vulnerability in RMA PDF filename formats

## Summary
Severity: High
Advisory: GHSA-7gh6-f4jh-3crq
CVE: CVE-2021-28583
CWE: CWE-657
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7gh6-f4jh-3crq
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.4.0 <2.4.2-p1
- Packagist: `magento/community-edition` — affected >=0 <2.3.7
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Magento versions 2.4.2 (and earlier), 2.4.1-p1 (and earlier) and 2.3.6-p1 (and earlier) are affected by a Violation of Secure Design Principles vulnerability in RMA PDF filename formats. Successful exploitation could allow an attacker to get unauthorized access to restricted resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28583
- https://github.com/magento/magento2/commit/1bd5cb8c065e44779526c0b044ce19b884707695
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-30.html
