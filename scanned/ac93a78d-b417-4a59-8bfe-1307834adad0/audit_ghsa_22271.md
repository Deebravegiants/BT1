# [H] Moodle Users could elevate their role when accessing the LTI tool on a provider site

## Summary
Severity: High
Advisory: GHSA-5wg9-5w3f-hxmh
CVE: CVE-2019-3849
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5wg9-5w3f-hxmh
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <3.4.8
- Packagist: `moodle/moodle` — affected >=3.5 <3.5.5
- Packagist: `moodle/moodle` — affected >=3.6 <3.6.3

## Details
A vulnerability was found in moodle before versions 3.6.3, 3.5.5 and 3.4.8. Users could assign themselves an escalated role within courses or content accessed via LTI, by modifying the request to the LTI publisher site.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3849
- https://github.com/moodle/moodle/commit/427463a52574e4b3bcbe1c65c49066438770641e
- https://github.com/moodle/moodle/commit/430f685834cef190bdf58afabe79e765d596890d
- https://github.com/moodle/moodle/commit/723d1a747555b795ed53a0fad01da455797bb78f
- https://github.com/moodle/moodle/commit/898d5d05a0c3ae6795db0241bf3cb5951213d45c
- https://github.com/moodle/moodle/commit/b77dcd23d8e39265b5c096f0d947764c02d832c8
- https://github.com/moodle/moodle/commit/cd3060d941a051931eb2613b25bafb0108665895
- https://github.com/moodle/moodle/commit/fba7dcd90abd45210d782a79c6e25bb3840c7438
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3849
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=384012#p1547744
