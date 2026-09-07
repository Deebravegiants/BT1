# [M] Moodle Authentication Bypass in Question-Bank

## Summary
Severity: Medium
Advisory: GHSA-3rqj-jchw-9cc7
CVE: CVE-2012-2356
CWE: CWE-288
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3rqj-jchw-9cc7
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.1 <2.1.6
- Packagist: `moodle/moodle` — affected >=2.2 <2.2.3

## Details
The question-bank functionality in Moodle 2.1.x before 2.1.6 and 2.2.x before 2.2.3 allows remote authenticated users to bypass intended capability requirements and save questions via a save_question action.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2356
- https://github.com/moodle/moodle/commit/0f83dd10a1d013e77906c7be4560126bb14c6b5c
- https://github.com/moodle/moodle/commit/29e247e44e983f230f248192ffac8e7b7abe37fd
- https://github.com/moodle/moodle/commit/51c5e6057c67687f5d872f8a228cfea275abf576
- https://github.com/moodle/moodle
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-32239
- http://openwall.com/lists/oss-security/2012/05/23/2
