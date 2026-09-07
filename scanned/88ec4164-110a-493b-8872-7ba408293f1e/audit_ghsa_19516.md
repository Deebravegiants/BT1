# [M] Moodle's AJAX section delete does not respect course_can_delete_section()

## Summary
Severity: Medium
Advisory: GHSA-cpm7-mv33-jwf8
CVE: CVE-2025-3644
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-04-25
Source: https://github.com/advisories/GHSA-cpm7-mv33-jwf8
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.18
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.12
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.8
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.4

## Details
A flaw was found in Moodle. Additional checks were required to prevent users from deleting course sections they did not have permission to modify.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3644
- https://access.redhat.com/security/cve/CVE-2025-3644
- https://bugzilla.redhat.com/show_bug.cgi?id=2359745
- https://github.com/moodle/moodle
- https://github.com/search?q=repo%3Amoodle%2Fmoodle+MDL-83994&type=commits
- https://moodle.org/mod/forum/discuss.php?d=467605
