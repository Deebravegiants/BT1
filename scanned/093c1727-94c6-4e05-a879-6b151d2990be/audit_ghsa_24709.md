# [M] Missing permission check in Moodle

## Summary
Severity: Medium
Advisory: GHSA-2m72-m5cw-3g9h
CVE: CVE-2021-20283
CWE: CWE-862, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2m72-m5cw-3g9h
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.10.0 <3.10.2
- Packagist: `moodle/moodle` — affected >=3.9.0 <3.9.5
- Packagist: `moodle/moodle` — affected >=3.8.0 <3.8.8
- Packagist: `moodle/moodle` — affected >=0 <3.5.17

## Details
The web service responsible for fetching other users' enrolled courses did not validate that the requesting user had permission to view that information in each course in moodle before 3.10.2, 3.9.5, 3.8.8, 3.5.17.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20283
- https://bugzilla.redhat.com/show_bug.cgi?id=1939051
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AFSNJ7XHVTC52RSRX2GBQFF3VEEAY2MS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UFH5DDMU5TZ3JT4Q52WMRAHACA5MHIMT
- https://moodle.org/mod/forum/discuss.php?d=419654
