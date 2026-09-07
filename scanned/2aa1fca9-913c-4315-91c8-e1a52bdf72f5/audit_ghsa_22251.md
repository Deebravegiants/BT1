# [M] Moodle allows attackers to obtain sensitive information

## Summary
Severity: Medium
Advisory: GHSA-fc5p-vj3h-x7g4
CVE: CVE-2014-0124
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-fc5p-vj3h-x7g4
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.4.9
- Packagist: `moodle/moodle` — affected >=2.5.0 <2.5.5
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.2

## Details
The identity-reporting implementations in mod/forum/renderer.php and mod/quiz/override_form.php in Moodle through 2.3.11, 2.4.x before 2.4.9, 2.5.x before 2.5.5, and 2.6.x before 2.6.2 do not properly restrict the display of e-mail addresses, which allows remote authenticated users to obtain sensitive information by using the (1) Forum or (2) Quiz module.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0124
- https://github.com/moodle/moodle/commit/2978623cda4521773fe2d45e04bee76601de487f
- https://github.com/moodle/moodle/commit/ae0ec61180ec71cb5b158633b0a3523a7ca41a82
- https://github.com/moodle/moodle/commit/db4e2c4cd47d48ebf06424d942bf603a8fa94d97
- https://github.com/moodle/moodle/commit/dc8f55c30211efd6fac80386e5b3bffef31cca13
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=256421
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-43916
- http://openwall.com/lists/oss-security/2014/03/17/1
