# [M] Moodle reveals student identities through assignment submissions search on anonymous submissions

## Summary
Severity: Medium
Advisory: GHSA-69m9-rprc-2x7g
CVE: CVE-2025-3628
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-04-25
Source: https://github.com/advisories/GHSA-69m9-rprc-2x7g
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.4

## Details
A flaw has was found in Moodle where anonymous assignment submissions can be de-anonymized via search, revealing student identities.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3628
- https://github.com/moodle/moodle/commit/5c703f7b4944dd0cc940ca20adfd91e6a2d98a66
- https://access.redhat.com/security/cve/CVE-2025-3628
- https://bugzilla.redhat.com/show_bug.cgi?id=2359706
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=467595
