# [M] Moodle allows IDOR when accessing the cohorts report

## Summary
Severity: Medium
Advisory: GHSA-34g7-pg9j-pxgp
CVE: CVE-2025-3647
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-04-25
Source: https://github.com/advisories/GHSA-34g7-pg9j-pxgp
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.18
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.12
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.8
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.4

## Details
A flaw was discovered in Moodle. Additional checks were required to ensure that users can only access cohort data they are authorized to retrieve.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3647
- https://github.com/moodle/moodle/commit/bd6ec0ac84cf0f73ab35e7e244e1f9b06929083a
- https://access.redhat.com/security/cve/CVE-2025-3647
- https://bugzilla.redhat.com/show_bug.cgi?id=2359762
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=467607
