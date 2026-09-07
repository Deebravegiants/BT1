# [M] Moodle has an IDOR in messaging web service which allows access to some user details

## Summary
Severity: Medium
Advisory: GHSA-pj96-xh2w-fgqx
CVE: CVE-2025-3645
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-04-25
Source: https://github.com/advisories/GHSA-pj96-xh2w-fgqx
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.18
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.12
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.8
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.4

## Details
A flaw was found in Moodle. Insufficient capability checks in a messaging web service allowed users to view other users' names and online statuses.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3645
- https://github.com/moodle/moodle/commit/2fd810c8981f9b10087467a3b8fce779b157200f
- https://github.com/moodle/moodle/commit/a8179842b450659c288f284e06361a4fbab8742a
- https://github.com/moodle/moodle/commit/bb65effe41524d8373c1dc499c3323ac469ea558
- https://access.redhat.com/security/cve/CVE-2025-3645
- https://bugzilla.redhat.com/show_bug.cgi?id=2359761
- https://github.com/moodle/moodle
- https://github.com/search?q=repo%3Amoodle%2Fmoodle+MDL-72704&type=commits
- https://moodle.org/mod/forum/discuss.php?d=467606
