# [M] Cross-site Scripting in moodle

## Summary
Severity: Medium
Advisory: GHSA-wpfp-q843-v772
CVE: CVE-2021-43558
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-11-23
Source: https://github.com/advisories/GHSA-wpfp-q843-v772
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.11.0 <3.11.4
- Packagist: `moodle/moodle` — affected >=3.10.0 <3.10.8
- Packagist: `moodle/moodle` — affected >=3.9.0 <3.9.11

## Details
A flaw was found in Moodle in versions 3.11 to 3.11.3, 3.10 to 3.10.7, 3.9 to 3.9.10 and earlier unsupported versions. A URL parameter in the filetype site administrator tool required extra sanitizing to prevent a reflected XSS risk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43558
- https://bugzilla.redhat.com/show_bug.cgi?id=2021515
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=429097
