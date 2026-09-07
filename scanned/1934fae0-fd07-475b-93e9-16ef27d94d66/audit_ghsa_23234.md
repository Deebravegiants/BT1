# [M] Magento DOM-based Cross-Site Scripting vulnerability on mage-messages cookies

## Summary
Severity: Medium
Advisory: GHSA-39ch-rg26-gmq5
CVE: CVE-2021-28556
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-39ch-rg26-gmq5
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.4.0 <2.4.2-p1
- Packagist: `magento/community-edition` — affected >=0 <2.3.7
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Magento versions 2.4.2 (and earlier), 2.4.1-p1 (and earlier) and 2.3.6-p1 (and earlier) are affected by a DOM-based Cross-Site Scripting vulnerability on mage-messages cookies. Successful exploitation could lead to arbitrary JavaScript execution by an unauthenticated attacker. User interaction is required for successful exploitation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28556
- https://github.com/magento/magento2/commit/1bd5cb8c065e44779526c0b044ce19b884707695
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-30.html
