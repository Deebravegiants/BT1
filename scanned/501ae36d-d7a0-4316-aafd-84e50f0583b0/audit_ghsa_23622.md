# [H] Microweber Discloses Sensitive Information

## Summary
Severity: High
Advisory: GHSA-pmxg-w9c7-ffmq
CVE: CVE-2020-13405
CWE: CWE-200, CWE-306
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pmxg-w9c7-ffmq
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0 <1.1.20

## Details
`userfiles/modules/users/controller/controller.php` in Microweber before 1.1.20 allows an unauthenticated user to disclose the users database via a `/modules/ POST` request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13405
- https://github.com/microweber/microweber/commit/269320e0e0e06a1785e1a1556da769a34280b7e6
- https://github.com/microweber/microweber
- https://rhinosecuritylabs.com/research/microweber-database-disclosure
