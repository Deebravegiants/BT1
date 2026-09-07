# [M] Moodle Lesson activity password bypass through PHP loose comparison

## Summary
Severity: Medium
Advisory: GHSA-xfv7-h2qg-rjm7
CVE: CVE-2024-45691
CWE: CWE-285, CWE-289
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-11-20
Source: https://github.com/advisories/GHSA-xfv7-h2qg-rjm7
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.13
- Packagist: `moodle/moodle` — affected >=4.2.0-beta <4.2.10
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.7
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.3

## Details
A flaw was found in Moodle. When restricting access to a lesson activity with a password, certain passwords could be bypassed or less secure due to a loose comparison in the password-checking logic. This issue only affected passwords set to "magic hash" values.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45691
- https://github.com/moodle/moodle/commit/3fc1073d304f660d2552b591c5fb92547ed01e92
- https://bugzilla.redhat.com/show_bug.cgi?id=2309940
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=461897#p1854494
- https://moodle.org/security
