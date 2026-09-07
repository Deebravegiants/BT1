# [M] Moodle Bypass email verification secret when confirming account registration

## Summary
Severity: Medium
Advisory: GHSA-grj4-g57c-9xmv
CVE: CVE-2021-20282
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-grj4-g57c-9xmv
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.5 <3.5.17
- Packagist: `moodle/moodle` — affected >=3.8 <3.8.8
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.5
- Packagist: `moodle/moodle` — affected >=3.10 <3.10.2

## Details
When creating a user account, it was possible to verify the account without having access to the verification email link/secret in moodle before 3.10.2, 3.9.5, 3.8.8, 3.5.17.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20282
- https://bugzilla.redhat.com/show_bug.cgi?id=1939046
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AFSNJ7XHVTC52RSRX2GBQFF3VEEAY2MS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UFH5DDMU5TZ3JT4Q52WMRAHACA5MHIMT
- https://moodle.org/mod/forum/discuss.php?d=419653
