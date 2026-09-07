# [M] Moodle allows remote authenticated users to reassign notes

## Summary
Severity: Medium
Advisory: GHSA-prrh-679x-79qh
CVE: CVE-2013-1834
CWE: CWE-284
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-prrh-679x-79qh
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=1.9.0 <2.2.8
- Packagist: `moodle/moodle` — affected >=2.3.0 <2.3.5
- Packagist: `moodle/moodle` — affected >=2.4.0 <2.4.2

## Details
notes/edit.php in Moodle 1.9.x through 1.9.19, 2.x through 2.1.10, 2.2.x before 2.2.8, 2.3.x before 2.3.5, and 2.4.x before 2.4.2 allows remote authenticated users to reassign notes via a modified (1) userid or (2) courseid field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1834
- https://github.com/moodle/moodle/commit/1b628c489def6e7394821f53a838591aa392e332
- https://github.com/moodle/moodle/commit/646059869e36ea1db844ee0884fb50020348dab1
- https://github.com/moodle/moodle/commit/6a9235c998dab2ec0ddc49898a59dd5089156cb0
- https://github.com/moodle/moodle/commit/a28da5d9b8221e53d3a0815fd0a1dc27bd48816b
- https://github.com/moodle/moodle/commit/bc144ebbe0a78a1ac854454246f26472ba0748b7
- https://github.com/moodle/moodle/commit/e13f286026056febba20e931d71134a2d145a091
- https://github.com/moodle/moodle/commit/ebfdc35f2a33f14051e22af5410485fe6f1afc92
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=225346
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-37411
- http://lists.fedoraproject.org/pipermail/package-announce/2013-April/101310.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-April/101358.html
- http://openwall.com/lists/oss-security/2013/03/25/2
