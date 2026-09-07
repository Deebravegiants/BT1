# [M] Moodle reflected XSS via H5P error message

## Summary
Severity: Medium
Advisory: GHSA-hjgc-jxjc-8v9j
CVE: CVE-2024-43439
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-11-11
Source: https://github.com/advisories/GHSA-hjgc-jxjc-8v9j
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.12
- Packagist: `moodle/moodle` — affected >=4.2.0-beta <4.2.9
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.6
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.2

## Details
A flaw was found in moodle. H5P error messages require additional sanitizing to prevent a reflected cross-site scripting (XSS) risk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-43439
- https://github.com/moodle/moodle/commit/c7d9026715a107ee16b9f9b2134ed4e6f667af99
- https://bugzilla.redhat.com/show_bug.cgi?id=2304268
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=461209
