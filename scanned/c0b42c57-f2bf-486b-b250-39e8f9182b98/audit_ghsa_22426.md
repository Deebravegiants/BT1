# [M] Moodle reveals absolute path in exception message

## Summary
Severity: Medium
Advisory: GHSA-xr24-jp5c-6c4v
CVE: CVE-2013-1831
CWE: CWE-200
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-xr24-jp5c-6c4v
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0
- Packagist: `moodle/moodle` — affected >=2.2.0 <2.2.8
- Packagist: `moodle/moodle` — affected >=2.3.0 <2.3.5
- Packagist: `moodle/moodle` — affected >=2.4.0 <2.4.2

## Details
lib/setuplib.php in Moodle through 2.1.10, 2.2.x before 2.2.8, 2.3.x before 2.3.5, and 2.4.x before 2.4.2 allows remote attackers to obtain sensitive information via an invalid request, which reveals the absolute path in an exception message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1831
- https://github.com/moodle/moodle/commit/2c7cdbb3b0b6ba4dd64297463d37a5acbd730216
- https://github.com/moodle/moodle/commit/53c66110a878f4f4644728138ea97c22990263e3
- https://github.com/moodle/moodle/commit/8d220cb552d9c55b98aef70e2f40ef560efeb79b
- https://github.com/moodle/moodle/commit/b3daaada49a2dd83a4f1e832465d5c318f9f275c
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=225342
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-36901
- http://lists.fedoraproject.org/pipermail/package-announce/2013-April/101310.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-April/101358.html
- http://openwall.com/lists/oss-security/2013/03/25/2
