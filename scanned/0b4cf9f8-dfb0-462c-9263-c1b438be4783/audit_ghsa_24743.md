# [H] Luracast Restler directory traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-rvmg-xc29-rvxf
CVE: CVE-2017-15363
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-rvmg-xc29-rvxf
Type: github-advisory

## Affected
- Packagist: `aoe/restler` — affected >=0 <1.7.1
- Packagist: `luracast/restler` — affected >=0 <3.1.0

## Details
Directory traversal vulnerability in public/examples/resources/getsource.php in Luracast Restler through 3.0.0, as used in the restler extension before 1.7.1 for TYPO3, allows remote attackers to read arbitrary files via the file parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15363
- https://extensions.typo3.org/extension/restler
- https://github.com/AOEpeople/TYPO3_Restler
- https://github.com/AOEpeople/TYPO3_Restler/releases/tag/1.7.1
