# [M] Quadratic blowup in Convert::xml2array()

## Summary
Severity: Medium
Advisory: GHSA-9fmg-89fx-r33w
CVE: CVE-2021-41559
CWE: CWE-776
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-29
Source: https://github.com/advisories/GHSA-9fmg-89fx-r33w
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=4.0.0 <4.10.9

## Details
Silverstripe silverstripe/framework 4.x until 4.10.9 has a quadratic blowup in Convert::xml2array() that enables a remote attack via a crafted XML document.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41559
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2021-41559.yaml
- https://github.com/silverstripe/silverstripe-framework/releases
- https://www.silverstripe.org/download/security-releases
- https://www.silverstripe.org/download/security-releases/cve-2021-41559
