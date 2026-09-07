# [M] Moodle remote code execution via quiz questions

## Summary
Severity: Medium
Advisory: GHSA-3m99-h3hp-w9j7
CVE: CVE-2014-3545
CWE: CWE-94
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3m99-h3hp-w9j7
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.1
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.4
- Packagist: `moodle/moodle` — affected >=2.5.0 <2.5.7
- Packagist: `moodle/moodle` — affected >=2.4.0 <2.4.11

## Details
Moodle through 2.3.11, 2.4.x before 2.4.11, 2.5.x before 2.5.7, 2.6.x before 2.6.4, and 2.7.x before 2.7.1 allows remote authenticated users to execute arbitrary code via a calculated question in a quiz.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3545
- https://github.com/moodle/moodle/commit/155bc7547227dc2047cfc8630cbfe121888b359b
- https://github.com/moodle/moodle/commit/29005a5418894b76e62e44bbc2c9e4ddee8f5ce6
- https://github.com/moodle/moodle/commit/44f726a7b1d351b39bb2a6a30c1b30027fabd000
- https://github.com/moodle/moodle/commit/539a25ff03fae377758d62caefcc71a2418e9a84
- https://github.com/moodle/moodle/commit/5c6c172033e3fb4afce862f8b32b459f5c35ad19
- https://github.com/moodle/moodle/commit/66de66fe6a8ce8f491562edad0a14f26d4808cb4
- https://github.com/moodle/moodle/commit/770d3ce42669067eca2bcee22d142ed7fec08550
- https://github.com/moodle/moodle/commit/82b3260eab2db58dfa9510645fd2c60ee0ce142e
- https://github.com/moodle/moodle/commit/88ec9f308da6a4bc7a735458cdf72648357d501d
- https://github.com/moodle/moodle
- https://github.com/moodle/moodle/blob/1474f74687dda57c7d011b92d16f25b9870d2799/question/type/calculated/question.php#L426
- https://moodle.org/mod/forum/discuss.php?d=264266
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-46148
- http://openwall.com/lists/oss-security/2014/07/21/1
