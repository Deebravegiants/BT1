# [M] PrestaShop file deletion via attachment API

## Summary
Severity: Medium
Advisory: GHSA-2rf5-3fw8-qm47
CVE: CVE-2023-39529
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2023-08-09
Source: https://github.com/advisories/GHSA-2rf5-3fw8-qm47
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=0 <8.1.1

## Details
### Impact
It is possible to delete a file from the server by using the Attachments controller and the Attachments API.

### Patches
8.1.1

### Found by
Kto94 (via Yeswehack)

### Workarounds
none

### References
none

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-2rf5-3fw8-qm47
- https://nvd.nist.gov/vuln/detail/CVE-2023-39529
- https://github.com/PrestaShop/PrestaShop/commit/b08c647305dc1e9e6a2445b724d13a9733b6ed82
- https://github.com/PrestaShop/PrestaShop
