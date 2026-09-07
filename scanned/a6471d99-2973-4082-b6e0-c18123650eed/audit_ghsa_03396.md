# [C] Backport for CVE-2021-21024 Blind SQLi from Magento 2

## Summary
Severity: Critical
Advisory: GHSA-fvrf-9428-527m
CVE: CVE-2021-21427
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-22
Source: https://github.com/advisories/GHSA-fvrf-9428-527m
Type: github-advisory

## Affected
- Packagist: `openmage/magento-lts` — affected >=0 <19.4.13
- Packagist: `openmage/magento-lts` — affected >=20.0.0 <20.0.9

## Details
### Impact
This vulnerability allows an administrator unauthorized access to restricted resources. 

We fixed a vulnerability in the MySQL adapter to prevent SQL injection attacks. This is a backport of CVE-2021-21024 https://helpx.adobe.com/security/products/magento/apsb21-08.html. 


### Patches
_Has the problem been patched? What versions should users upgrade to?_
> v20.0.9 v19.4.13

## References
- https://github.com/OpenMage/magento-lts/security/advisories/GHSA-fvrf-9428-527m
- https://nvd.nist.gov/vuln/detail/CVE-2021-21427
