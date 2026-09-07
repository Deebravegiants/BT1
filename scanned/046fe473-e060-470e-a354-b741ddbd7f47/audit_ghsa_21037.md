# [M] Moodle type juggling vulnerability

## Summary
Severity: Medium
Advisory: GHSA-2jxg-mv2m-j4r7
CVE: CVE-2021-40693
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-09-30
Source: https://github.com/advisories/GHSA-2jxg-mv2m-j4r7
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.10
- Packagist: `moodle/moodle` — affected >=3.10 <3.10.7
- Packagist: `moodle/moodle` — affected >=3.11 <3.11.3

## Details
An authentication bypass risk was identified in the external database authentication functionality, due to a type juggling vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40693
- https://bugzilla.redhat.com/show_bug.cgi?id=2043417
- https://github.com/moodle/moodle
