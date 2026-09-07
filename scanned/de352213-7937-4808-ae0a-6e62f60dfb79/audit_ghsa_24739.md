# [M] Moodle allows attackers to modify "Exclude grade" settings

## Summary
Severity: Medium
Advisory: GHSA-32hg-73hp-vwc8
CVE: CVE-2016-2155
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-32hg-73hp-vwc8
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.11
- Packagist: `moodle/moodle` — affected >=2.9.0 <2.9.5
- Packagist: `moodle/moodle` — affected >=3.0.0 <3.0.3

## Details
The grade-reporting feature in Singleview (aka Single View) in Moodle 2.8.x before 2.8.11, 2.9.x before 2.9.5, and 3.0.x before 3.0.3 does not consider the moodle/grade:manage capability, which allows remote authenticated users to modify "Exclude grade" settings by leveraging the Non-Editing Instructor role.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2155
- https://github.com/moodle/moodle/commit/3328dc32a75d6aa4bc92865fa236dc6d52dcb7bf
- https://github.com/moodle/moodle/commit/5208032b23b7999d7048a3da7a4b70c038d93506
- https://github.com/moodle/moodle/commit/71beedee8c82c378ed10a0569c8b19ec641df9e3
- https://github.com/moodle/moodle/commit/ad67b7eeea4abf194eb432d5958e9a7032ee2c25
- https://github.com/moodle/moodle/commit/ae66ed23b6ae8000efd4e1f612697892c9795c65
- https://github.com/moodle/moodle/commit/b74d0f8404651d9ad0d97fd7eb58a94079342eb3
- https://github.com/moodle/moodle/commit/c7f7b18adecb4a80c4f3defee31e72e591133693
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=330177
- https://web.archive.org/web/20160424224349/http://www.securitytracker.com/id/1035333
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-52378
- http://www.openwall.com/lists/oss-security/2016/03/21/1
