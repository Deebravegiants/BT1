# [M] Moodle course access permissions are not properly checked in course_output_fragment_course_overview

## Summary
Severity: Medium
Advisory: GHSA-rjcm-7v2p-9265
CVE: CVE-2025-62393
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-10-23
Source: https://github.com/advisories/GHSA-rjcm-7v2p-9265
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=5.0.0-beta <5.0.3

## Details
A flaw was found in the course overview output function where user access permissions were not fully enforced. This could allow unauthorized users to view information about courses they should not have access to, potentially exposing limited course details.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62393
- https://github.com/moodle/moodle/commit/fc69b4744ba0132cc3093fd81940be15bc293835
- https://access.redhat.com/security/cve/CVE-2025-62393
- https://bugzilla.redhat.com/show_bug.cgi?id=2404426
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=470381
