# [M] Moodle Private files uploaded via incoming mail processing could bypass quota restrictions

## Summary
Severity: Medium
Advisory: GHSA-j8wr-7xxj-c2fr
CVE: CVE-2019-10134
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-j8wr-7xxj-c2fr
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.6 <3.6.4
- Packagist: `moodle/moodle` — affected >=3.5 <3.5.6
- Packagist: `moodle/moodle` — affected >=3.4 <3.4.9
- Packagist: `moodle/moodle` — affected >=3.1 <3.1.18

## Details
A flaw was found in Moodle before 3.7, 3.6.4, 3.5.6, 3.4.9 and 3.1.18. The size of users' private file uploads via email were not correctly checked, so their quota allowance could be exceeded.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10134
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10134
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=386524
