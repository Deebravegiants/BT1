# [C] Moodle PostScript Code Injection

## Summary
Severity: Critical
Advisory: GHSA-xp2f-9mx3-3c6p
CVE: CVE-2022-35649
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-26
Source: https://github.com/advisories/GHSA-xp2f-9mx3-3c6p
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.15
- Packagist: `moodle/moodle` — affected >=3.11 <3.11.8
- Packagist: `moodle/moodle` — affected >=4.0 <4.0.2

## Details
The vulnerability was found in Moodle, occurs due to improper input validation when parsing PostScript code. An omitted execution parameter results in a remote code execution risk for sites running GhostScript versions older than 9.50. Successful exploitation of this vulnerability may result in complete compromise of vulnerable system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35649
- https://bugzilla.redhat.com/show_bug.cgi?id=2106273
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6MOKYVRNFNAODP2XSMGJ5CRDUZCZKAR3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MTKUSFPSYFINSQFSOHDQIDVE6FWBEU6V
- https://moodle.org/mod/forum/discuss.php?d=436456
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-75044
