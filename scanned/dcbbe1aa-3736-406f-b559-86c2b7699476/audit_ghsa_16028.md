# [H] Moodle has CSRF risk in Feedback non-respondents report

## Summary
Severity: High
Advisory: GHSA-x87r-37q5-mmr8
CVE: CVE-2024-43434
CWE: CWE-22, CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-11-07
Source: https://github.com/advisories/GHSA-x87r-37q5-mmr8
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.12
- Packagist: `moodle/moodle` — affected >=4.2.0-beta <4.2.9
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.6
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.2

## Details
The bulk message sending feature in Moodle's Feedback module's non-respondents report had an incorrect CSRF token check, leading to a CSRF vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-43434
- https://bugzilla.redhat.com/show_bug.cgi?id=2304262
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=461203
