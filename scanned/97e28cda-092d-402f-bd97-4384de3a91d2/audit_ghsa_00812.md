# [H] Observable Timing Discrepancy in OpenMage LTS

## Summary
Severity: High
Advisory: GHSA-crf2-xm6x-46p6
CVE: CVE-2020-15151
CWE: CWE-203, CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-08-19
Source: https://github.com/advisories/GHSA-crf2-xm6x-46p6
Type: github-advisory

## Affected
- Packagist: `openmage/magento-lts` — affected >=0 <19.4.6
- Packagist: `openmage/magento-lts` — affected >=20.0.0 <20.0.2

## Details
### Impact
This vulnerability allows to circumvent the **formkey protection** in the Admin Interface and increases the attack surface for  **Cross Site Request Forgery** attacks 

### Patches
The latest OpenMage Versions up from 19.4.6 and 20.0.2 have this Issue solved


### References
Related to Adobes CVE-2020-9690 ( https://helpx.adobe.com/security/products/magento/apsb20-47.html )
fixed in Magento2 https://github.com/magento/magento2/commit/52d72b8010c9cecb5b8e3d98ec5edc1ddcc65fb4
as part of 2.4.0/2.3.5-p2

## References
- https://github.com/OpenMage/magento-lts/security/advisories/GHSA-crf2-xm6x-46p6
- https://nvd.nist.gov/vuln/detail/CVE-2020-15151
- https://github.com/OpenMage/magento-lts/commit/7c526bc6a6a51b57a1bab4c60f104dc36cde347a
- https://github.com/OpenMage/magento-lts
- https://helpx.adobe.com/security/products/magento/apsb20-47.html
