# [M] Moodle does not enforce capability requirements for reading blog comments

## Summary
Severity: Medium
Advisory: GHSA-wp3g-pr4h-q6vv
CVE: CVE-2013-2082
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wp3g-pr4h-q6vv
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.2.10
- Packagist: `moodle/moodle` — affected >=2.3.0 <2.3.7
- Packagist: `moodle/moodle` — affected >=2.4.0 <2.4.4

## Details
Moodle through 2.1.10, 2.2.x before 2.2.10, 2.3.x before 2.3.7, and 2.4.x before 2.4.4 does not enforce capability requirements for reading blog comments, which allows remote attackers to obtain sensitive information via a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2082
- https://github.com/moodle/moodle/commit/28772fb9e7e6be01b765fb721af16901bb47e417
- https://github.com/moodle/moodle/commit/5fde58a59335bc3109a9eaac4a15d1e9217541c3
- https://github.com/moodle/moodle/commit/8aa12adcf26ff2f0b61cd6f0288f2886c8c55bf7
- https://github.com/moodle/moodle/commit/9a909b1a359f72b8d384e18da8e05474604279e1
- https://github.com/moodle/moodle/commit/cb538f0e539e833edb7cf6fa3d705e8abc5003fd
- https://github.com/moodle/moodle/commit/f9e27e8323f31186820d25252ec0d4c6cd65dafc
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=228934
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-37245
- http://lists.fedoraproject.org/pipermail/package-announce/2013-May/106965.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-May/106988.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-May/107026.html
- http://openwall.com/lists/oss-security/2013/05/21/1
