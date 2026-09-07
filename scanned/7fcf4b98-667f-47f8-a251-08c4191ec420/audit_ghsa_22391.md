# [M] Moodle CRLF Injection Vulnerability in Calendar Component

## Summary
Severity: Medium
Advisory: GHSA-4w8m-96v9-2c86
CVE: CVE-2011-4203
CWE: CWE-113, CWE-93
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4w8m-96v9-2c86
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <1.9.15
- Packagist: `moodle/moodle` — affected >=2.0 <2.0.6
- Packagist: `moodle/moodle` — affected >=2.1 <2.1.3

## Details
CRLF injection vulnerability in calendar/set.php in the Calendar component in Moodle 1.9.x before 1.9.15, 2.0.x before 2.0.6, 2.1.x before 2.1.3, and 2.2 allows remote attackers to inject arbitrary HTTP headers and conduct HTTP response splitting attacks via vectors involving the url variable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4203
- https://github.com/moodle/moodle/commit/581e8dba387f090d89382115fd850d8b44351526
- https://github.com/moodle/moodle/commit/ae7cc577b7115a7ad7a68dc4986aca9e2bda2cf5
- https://github.com/moodle/moodle/commit/bc577df6a974606fcb0882b090b00ea5a4e10cf6
- https://github.com/moodle/moodle/commit/e311b14364719b0f7851149ee51c1a4ec732635e
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=191754
- http://penturalabs.wordpress.com/2011/12/13/advisory-crlf-injection-vulnerability-in-moodle
