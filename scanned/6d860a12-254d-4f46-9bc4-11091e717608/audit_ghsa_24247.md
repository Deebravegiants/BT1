# [M] Codiad Cross-site Scripting Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g2x4-256v-5pvx
CVE: CVE-2020-14042
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-g2x4-256v-5pvx
Type: github-advisory

## Affected
- Packagist: `codiad/codiad` — affected >=1.7.8

## Details
A Cross Site Scripting (XSS) vulnerability was found in Codiad v1.7.8 and later. The vulnerability occurs because of improper sanitization of the folder's name `$path` variable in components/filemanager/class.filemanager.php. **NOTE:** the vendor states "Codiad is no longer under active maintenance by core contributors."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14042
- https://github.com/Codiad/Codiad/issues/1122
- https://github.com/Codiad/Codiad/issues/1132
- https://github.com/Codiad/Codiad
- https://web.archive.org/web/20220828225621/https://advisory.checkmarx.net/advisory/CX-2020-4278
