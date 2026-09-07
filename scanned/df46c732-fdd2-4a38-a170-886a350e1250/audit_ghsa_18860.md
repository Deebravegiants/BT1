# [M] Moodle sends quiz-related messages to inactive/suspended users

## Summary
Severity: Medium
Advisory: GHSA-8fcv-4qp9-pg32
CVE: CVE-2025-62394
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-10-23
Source: https://github.com/advisories/GHSA-8fcv-4qp9-pg32
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=5.0.0-beta <5.0.3
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.7

## Details
Moodle failed to verify enrolment status correctly when sending quiz notifications. As a result, suspended or inactive users might receive quiz-related messages, leaking limited course information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62394
- https://github.com/moodle/moodle/commit/022bfbfb564d8f3866a43d26eed215213bbdd28a
- https://access.redhat.com/security/cve/CVE-2025-62394
- https://bugzilla.redhat.com/show_bug.cgi?id=2404427
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=470383
