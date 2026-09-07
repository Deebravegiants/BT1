# [M] infusionsoft-php-sdk reflected Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-8jmj-4p32-mc9p
CVE: CVE-2017-6216
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8jmj-4p32-mc9p
Type: github-advisory

## Affected
- Packagist: `novaksolutions/infusionsoft-php-sdk` — affected >=0 <1.0

## Details
novaksolutions/infusionsoft-php-sdk before v1.0 is vulnerable to a reflected XSS in the `leadscoring.php` via `ContactId` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6216
- https://github.com/novaksolutions/infusionsoft-php-sdk/issues/111
- https://github.com/novaksolutions/infusionsoft-php-sdk/commit/110c06ffe0cdff3d8eb3ad2080eb2a5b83a916a5
- https://github.com/novaksolutions/infusionsoft-php-sdk
