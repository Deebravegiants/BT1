# [M] Moodle contains Stored XSS via ID number user profile field

## Summary
Severity: Medium
Advisory: GHSA-h7h6-fwpv-ggvx
CVE: CVE-2021-20279
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h7h6-fwpv-ggvx
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.10 <3.10.2
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.5
- Packagist: `moodle/moodle` — affected >=3.8 <3.8.8
- Packagist: `moodle/moodle` — affected >=3.5 <3.5.17

## Details
The ID number user profile field required additional sanitizing to prevent a stored XSS risk in moodle before 3.10.2, 3.9.5, 3.8.8, 3.5.17.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20279
- https://github.com/moodle/moodle/commit/a7e0ba1e71205ccb0a73dedee414f1a167ee2ed7
- https://bugzilla.redhat.com/show_bug.cgi?id=1939033
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AFSNJ7XHVTC52RSRX2GBQFF3VEEAY2MS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UFH5DDMU5TZ3JT4Q52WMRAHACA5MHIMT
- https://moodle.org/mod/forum/discuss.php?d=419650
