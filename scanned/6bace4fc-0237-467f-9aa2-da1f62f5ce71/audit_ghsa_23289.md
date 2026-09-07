# [M] Moodle does not properly restrict access

## Summary
Severity: Medium
Advisory: GHSA-2vhr-4mhq-m35c
CVE: CVE-2014-0123
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-2vhr-4mhq-m35c
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.4.9
- Packagist: `moodle/moodle` — affected >=2.5.0 <2.5.5
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.2

## Details
The wiki subsystem in Moodle through 2.3.11, 2.4.x before 2.4.9, 2.5.x before 2.5.5, and 2.6.x before 2.6.2 does not properly restrict (1) view and (2) edit access, which allows remote authenticated users to perform wiki operations by leveraging the student role and using the Recent Activity block to reach the individual wiki of an arbitrary student.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0123
- https://github.com/moodle/moodle/commit/3a7b9b76c2d3c58237bec56b3b537e05c23970ad
- https://github.com/moodle/moodle/commit/d9596365e59ac53787105ff326f7f2bab5b9bada
- https://github.com/moodle/moodle/commit/e6499fb8a4463b1130babb09c42f3d5559276d17
- https://github.com/moodle/moodle/commit/fa0777902633b54ca5566dd8af304ce5587051e5
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=256419
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-39990
- http://openwall.com/lists/oss-security/2014/03/17/1
