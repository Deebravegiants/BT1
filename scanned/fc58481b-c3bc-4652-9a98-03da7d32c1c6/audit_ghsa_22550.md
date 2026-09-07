# [M] Moodle is vulnerable to Sensitive Information Disclosure

## Summary
Severity: Medium
Advisory: GHSA-wmmc-qjq2-vvm2
CVE: CVE-2013-2080
CWE: CWE-200
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wmmc-qjq2-vvm2
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.3.7
- Packagist: `moodle/moodle` — affected >=2.4.0 <2.4.4

## Details
The core_grade component in Moodle through 2.2.10, 2.3.x before 2.3.7, and 2.4.x before 2.4.4 does not properly consider the existence of hidden grades, which allows remote authenticated users to obtain sensitive information by leveraging the student role and reading the Gradebook Overview report.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2080
- https://github.com/moodle/moodle/commit/4b280ca67972479b4b86dd8861bcbeb8c06e41f9
- https://github.com/moodle/moodle/commit/5df9bc3998095299c6862973866252649a5e0866
- https://github.com/moodle/moodle/commit/bf5f227817ec65cfdf76d4bdc961af81a701bc31
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=228931
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-37475
- http://lists.fedoraproject.org/pipermail/package-announce/2013-May/106965.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-May/106988.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-May/107026.html
- http://openwall.com/lists/oss-security/2013/05/21/1
