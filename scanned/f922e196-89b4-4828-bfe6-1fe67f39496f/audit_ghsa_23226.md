# [H] Moodle vulnerable to RCE

## Summary
Severity: High
Advisory: GHSA-vr6v-g96p-cjc3
CVE: CVE-2020-10738
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vr6v-g96p-cjc3
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.8 <3.8.3
- Packagist: `moodle/moodle` — affected >=3.7 <3.7.6
- Packagist: `moodle/moodle` — affected >=3.6 <3.6.10
- Packagist: `moodle/moodle` — affected >=3.5 <3.5.12

## Details
A flaw was found in Moodle versions 3.8 before 3.8.3, 3.7 before 3.7.6, 3.6 before 3.6.10, 3.5 before 3.5.12 and earlier unsupported versions. It was possible to create a SCORM package in such a way that when added to a course, it could be interacted with via web services in order to achieve remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10738
- https://github.com/moodle/moodle/commit/2cd534a7df3867813e3aad42db615865149a58c6
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10738
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=403513
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-68410
