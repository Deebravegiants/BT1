# [M] Moodle stored Cross-site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-mgfp-qcf2-pw3m
CVE: CVE-2020-25627
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mgfp-qcf2-pw3m
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.2

## Details
The moodlenetprofile user profile field required extra sanitizing to prevent a stored XSS risk. This affects versions 3.9 to 3.9.1. Fixed in 3.9.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25627
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=410839
