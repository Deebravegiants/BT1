# [M] Moodle is vulnerable to unauthorized new accounts creation

## Summary
Severity: Medium
Advisory: GHSA-966m-m549-2878
CVE: CVE-2010-1616
CWE: CWE-284
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-966m-m549-2878
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=1.8.0 <1.8.12
- Packagist: `moodle/moodle` — affected >=1.9.0 <1.9.8

## Details
Moodle 1.8.x and 1.9.x before 1.9.8 can create new roles when restoring a course, which allows teachers to create new accounts even if they do not have the moodle/user:create capability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-1616
- https://github.com/moodle/moodle/commit/55f5b2e8b84e6390c0917195d01a3b34c33ff398
- https://github.com/moodle/moodle/commit/5d9ab024ac9c311c84716628cce9a124173a2e8b
- https://github.com/moodle/moodle/commit/5e934890c9fbe28bf89362d3eb6140208b5e3464
- https://github.com/moodle/moodle/commit/b0ccfc5ce87f09d4df814b057f5e6820d37fdad1
- https://github.com/moodle/moodle/commit/d8ada21339ecc147eccaaae97678f5368ac05f8b
- https://github.com/moodle/moodle
- http://lists.opensuse.org/opensuse-security-announce/2010-05/msg00001.html
- http://moodle.org/security
- http://tracker.moodle.org/browse/MDL-16658
- http://www.vupen.com/english/advisories/2010/1107
