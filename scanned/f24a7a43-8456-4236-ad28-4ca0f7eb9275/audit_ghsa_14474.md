# [C] Moodle's Mustache pix helper contained a potential Mustache injection risk if combined with user input

## Summary
Severity: Critical
Advisory: GHSA-q2x3-2f9g-h559
CVE: CVE-2023-28333
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-23
Source: https://github.com/advisories/GHSA-q2x3-2f9g-h559
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.1.0 <4.1.2
- Packagist: `moodle/moodle` — affected >=4.0.0 <4.0.7
- Packagist: `moodle/moodle` — affected >=3.11.0 <3.11.13
- Packagist: `moodle/moodle` — affected >=0 <3.9.20

## Details
The Mustache pix helper contained a potential Mustache injection risk if combined with user input (note: This did not appear to be implemented/exploitable anywhere in the core Moodle LMS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28333
- https://github.com/moodle/moodle/commit/128c0c21607a71f411611a0104b2a8c858dd6fca
- https://bugzilla.redhat.com/show_bug.cgi?id=2179422
- https://git.moodle.org/gw?p=moodle.git;a=commitdiff;h=128c0c21607a71f411611a0104b2a8c858dd6fca
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3QZN34VSF4HTCW3C3ZP2OZYSLYUKADPF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3QZN34VSF4HTCW3C3ZP2OZYSLYUKADPF
- https://moodle.org/mod/forum/discuss.php?d=445065
