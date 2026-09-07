# [M] Moodle allows attackers to obtain username and course information

## Summary
Severity: Medium
Advisory: GHSA-4c5g-w3gf-rf4f
CVE: CVE-2014-3546
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4c5g-w3gf-rf4f
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.4.11
- Packagist: `moodle/moodle` — affected >=2.5.0 <2.5.7
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.4
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.1

## Details
Moodle through 2.3.11, 2.4.x before 2.4.11, 2.5.x before 2.5.7, 2.6.x before 2.6.4, and 2.7.x before 2.7.1 does not enforce certain capability requirements in (1) notes/index.php and (2) user/edit.php, which allows remote attackers to obtain potentially sensitive username and course information via a modified URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3546
- https://github.com/moodle/moodle/commit/2ca9e09dab3ff374e1026780b23c63751f4ee312
- https://github.com/moodle/moodle/commit/74556525de9617c593c3e08269d6d541c6576c90
- https://github.com/moodle/moodle/commit/8f7d596058a18c60b795b4677b59cf074c56de39
- https://github.com/moodle/moodle/commit/9dbf62d23017a91fcbf63bba7f2eb4835f77b8c9
- https://github.com/moodle/moodle/commit/dc97145785b9ae192168659c65309bca61a58151
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=264267
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-45760
- http://openwall.com/lists/oss-security/2014/07/21/1
