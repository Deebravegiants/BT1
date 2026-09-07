# [M] Moodle Users Can Bypass Deleted Status

## Summary
Severity: Medium
Advisory: GHSA-72gv-qqrp-h9qg
CVE: CVE-2012-0797
CWE: CWE-287
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-72gv-qqrp-h9qg
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.2 <2.2.1
- Packagist: `moodle/moodle` — affected >=2.1 <2.1.4
- Packagist: `moodle/moodle` — affected >=2.0 <2.0.7

## Details
The webservices functionality in Moodle 2.0.x before 2.0.7, 2.1.x before 2.1.4, and 2.2.x before 2.2.1 allows remote authenticated users to bypass the deleted status and continue using a server via a token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-0797
- https://github.com/moodle/moodle/commit/364622b4662d9f349f3701ed548cda2f31491fea
- https://github.com/moodle/moodle/commit/bbcde38b334ecbfa2a18b01b77a7e995b2c0d9f7
- https://github.com/moodle/moodle/commit/dbfa519ad9e4d33ac3a4cd506d606d56a2f0bbff
- https://github.com/moodle/moodle/commit/e922d9a90bab337b1082fbe28c352c18cae2580e
- https://bugzilla.redhat.com/show_bug.cgi?id=783532
- https://github.com/moodle/moodle
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-28126
- http://moodle.org/mod/forum/discuss.php?d=194016
