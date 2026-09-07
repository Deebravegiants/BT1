# [H] RCE via PHP Object injection via SOAP Requests

## Summary
Severity: High
Advisory: GHSA-jrgf-vfw2-hj26
CVE: CVE-2020-15244
CWE: CWE-502, CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2020-10-30
Source: https://github.com/advisories/GHSA-jrgf-vfw2-hj26
Type: github-advisory

## Affected
- Packagist: `openmage/magento-lts` — affected >=0 <19.4.8
- Packagist: `openmage/magento-lts` — affected >=20.0.0 <20.0.4

## Details
### Impact
This vulnerability allows an admin user to generate soap credentials that can be used to trigger RCE via PHP Object Injection through product attributes and a product.

### Patches
The latest OpenMage Versions up from 19.4.7 and 20.0.3 have this Issue solved

### Credits
Credit to Luke Rodgers for reporting

## References
- https://github.com/OpenMage/magento-lts/security/advisories/GHSA-jrgf-vfw2-hj26
- https://nvd.nist.gov/vuln/detail/CVE-2020-15244
- https://github.com/OpenMage/magento-lts/commit/26433d15b57978fcb7701b5f99efe8332ca8630b
- https://github.com/OpenMage/magento-lts
