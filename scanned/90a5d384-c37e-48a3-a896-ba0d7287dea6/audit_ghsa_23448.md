# [H] Moodle all messaging conversations could be viewed

## Summary
Severity: High
Advisory: GHSA-ww45-x87c-wgff
CVE: CVE-2019-10154
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-ww45-x87c-wgff
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.6 <3.6.4

## Details
A flaw was found in Moodle before versions 3.7, 3.6.4. A web service fetching messages was not restricted to the current user's conversations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10154
- https://github.com/moodle/moodle/commit/2904a7f851da8e66be12f41d55068bf07817fbd6
- https://github.com/moodle/moodle/commit/a3d19efab4aff83c07db9f0ad34c8f0e1f29c64c
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10154
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=386521
