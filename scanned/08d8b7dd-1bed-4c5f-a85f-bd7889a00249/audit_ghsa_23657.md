# [M] Moodle allows discovery of an author's username

## Summary
Severity: Medium
Advisory: GHSA-p5j7-26wj-423j
CVE: CVE-2014-3617
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-p5j7-26wj-423j
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.5.8
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.5
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.2

## Details
The forum_print_latest_discussions function in mod/forum/lib.php in Moodle through 2.4.11, 2.5.x before 2.5.8, 2.6.x before 2.6.5, and 2.7.x before 2.7.2 allows remote authenticated users to bypass the individual answer-posting requirement without the mod/forum:viewqandawithoutposting capability, and discover an author's username, by leveraging the student role and visiting a Q&A forum.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3617
- https://github.com/moodle/moodle/commit/1c5d2aefd1c6706176e97b99b2f9deef582564be
- https://github.com/moodle/moodle/commit/1f3066f1977cf9ba36bb2583597af8bc53eb7d0f
- https://github.com/moodle/moodle/commit/532c25d5bd6d0f2ad14720fcee0da8c879c4d0f2
- https://github.com/moodle/moodle/commit/8f2e80600bf0fc220b92706907fb3d683602e5c2
- https://github.com/moodle/moodle/commit/95c3874b717e19711780147c29285e56ca01ff79
- https://github.com/moodle/moodle/commit/982c8524dd27066a6893a4b2ff2c41d60f9bdc23
- https://github.com/moodle/moodle/commit/a80ed84ed37d24e564b0bb7b8d51c4206b1fcd54
- https://github.com/moodle/moodle/commit/b1325427ecefb23002d3c79a7222e98f3995c0fb
- https://github.com/moodle/moodle/commit/b2b8d932f11c089b59b6c5ce439487ae3e5d79aa
- https://github.com/moodle/moodle/commit/ebbff905629fbd87a6a81cc471964e995fba3eb0
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=269591
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-46619
- http://openwall.com/lists/oss-security/2014/09/15/1
