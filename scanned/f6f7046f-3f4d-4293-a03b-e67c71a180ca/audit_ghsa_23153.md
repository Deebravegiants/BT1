# [M] Moodle Arbitrary File Read via Backup Functionality

## Summary
Severity: Medium
Advisory: GHSA-cr78-rphw-w73p
CVE: CVE-2012-6099
CWE: CWE-20
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-cr78-rphw-w73p
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.4 <2.4.1
- Packagist: `moodle/moodle` — affected >=2.3 <2.3.4
- Packagist: `moodle/moodle` — affected >=2.2 <2.2.7
- Packagist: `moodle/moodle` — affected >=2.1 <2.1.10

## Details
The moodle1 backup converter in `backup/converter/moodle1/lib.php` in Moodle 2.1.x before 2.1.10, 2.2.x before 2.2.7, 2.3.x before 2.3.4, and 2.4.x before 2.4.1 does not properly validate pathnames, which allows remote authenticated users to read arbitrary files by leveraging the backup-restoration feature.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-6099
- https://github.com/moodle/moodle/commit/0ab681d3e7bed2a37430387f9da8504c0b077d10
- https://github.com/moodle/moodle/commit/7b66137f7bcc84fb5eb07f58fb658b21bf37cc44
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=220160
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-36977
- http://openwall.com/lists/oss-security/2013/01/21/1
