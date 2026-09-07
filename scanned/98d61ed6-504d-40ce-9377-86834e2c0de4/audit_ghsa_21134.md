# [H] Moodle Arbitrary file read when importing lesson questions

## Summary
Severity: High
Advisory: GHSA-pgm5-cr62-prxq
CVE: CVE-2022-35650
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-07-26
Source: https://github.com/advisories/GHSA-pgm5-cr62-prxq
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.15
- Packagist: `moodle/moodle` — affected >=3.11 <3.11.8
- Packagist: `moodle/moodle` — affected >=4.0 <4.0.2

## Details
The vulnerability was found in Moodle, occurs due to input validation error when importing lesson questions. This insufficient path checks results in arbitrary file read risk. This vulnerability allows a remote attacker to perform directory traversal attacks. The capability to access this feature is only available to teachers, managers and admins by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35650
- https://bugzilla.redhat.com/show_bug.cgi?id=2106274
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6MOKYVRNFNAODP2XSMGJ5CRDUZCZKAR3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MTKUSFPSYFINSQFSOHDQIDVE6FWBEU6V
- https://moodle.org/mod/forum/discuss.php?d=436457
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-72029
