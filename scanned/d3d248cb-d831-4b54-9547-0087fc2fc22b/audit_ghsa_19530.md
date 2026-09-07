# [M] Moodle self enrollment available before completing second factor with MFA enabled

## Summary
Severity: Medium
Advisory: GHSA-qhc7-xhc2-7p7w
CVE: CVE-2025-3634
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-04-25
Source: https://github.com/advisories/GHSA-qhc7-xhc2-7p7w
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.12
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.8
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.4

## Details
A security vulnerability was discovered in Moodle that allows students to enroll themselves in courses without completing all the necessary safety checks. Specifically, users can sign up for courses prematurely, even if they haven't finished two-step verification processes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3634
- https://github.com/moodle/moodle/commit/b0965139014b459c3cb96e4fff45af4d5e09e261
- https://access.redhat.com/security/cve/CVE-2025-3634
- https://bugzilla.redhat.com/show_bug.cgi?id=2359707
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=467596
