# [M] Moodle allowed some users without permission to view other users' full names

## Summary
Severity: Medium
Advisory: GHSA-93wh-35r4-6qmw
CVE: CVE-2021-20281
CWE: CWE-200, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-03-29
Source: https://github.com/advisories/GHSA-93wh-35r4-6qmw
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.10.0 <3.10.2
- Packagist: `moodle/moodle` — affected >=3.9.0 <3.9.5
- Packagist: `moodle/moodle` — affected >=3.8.0 <3.8.8
- Packagist: `moodle/moodle` — affected >=3.5 <3.5.17

## Details
It was possible for some users without permission to view other users' full names to do so via the online users block in moodle before 3.10.2, 3.9.5, 3.8.8, 3.5.17.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20281
- https://github.com/moodle/moodle/commit/33d6017287e1835513a3de8edd3fbf7a6a90af9c
- https://bugzilla.redhat.com/show_bug.cgi?id=1939041
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AFSNJ7XHVTC52RSRX2GBQFF3VEEAY2MS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UFH5DDMU5TZ3JT4Q52WMRAHACA5MHIMT
- https://moodle.org/mod/forum/discuss.php?d=419652
