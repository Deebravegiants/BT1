# [H] Codiad CSRF Vulnerability

## Summary
Severity: High
Advisory: GHSA-35gp-jxw8-xw6h
CVE: CVE-2020-14043
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-35gp-jxw8-xw6h
Type: github-advisory

## Affected
- Packagist: `codiad/codiad` — affected >=1.7.8

## Details
A Cross Side Request Forgery (CSRF) vulnerability was found in Codiad v1.7.8 and later. The request to download a plugin from the marketplace is only available to admin users and it isn't CSRF protected in components/market/controller.php. This might cause admins to make a vulnerable request without them knowing and result in remote code execution. **NOTE:** the vendor states "Codiad is no longer under active maintenance by core contributors."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14043
- https://github.com/Codiad/Codiad/issues/1122
- https://github.com/Codiad/Codiad/issues/1132
- https://github.com/Codiad/Codiad
- https://web.archive.org/web/20220828222205/https://advisory.checkmarx.net/advisory/CX-2020-4279
