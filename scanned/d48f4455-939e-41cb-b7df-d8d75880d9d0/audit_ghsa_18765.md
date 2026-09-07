# [M] Moodle exposed the names of hidden groups to users

## Summary
Severity: Medium
Advisory: GHSA-422v-w6c5-vq42
CVE: CVE-2025-62400
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-10-23
Source: https://github.com/advisories/GHSA-422v-w6c5-vq42
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=5.0.0-beta <5.0.3
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.7
- Packagist: `moodle/moodle` — affected >=4.2.0-beta <4.4.11
- Packagist: `moodle/moodle` — affected >=0 <4.1.21

## Details
Moodle exposed the names of hidden groups to users who had permission to create calendar events but not to view hidden groups. This could reveal private or restricted group information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62400
- https://github.com/moodle/moodle/commit/0c70d67059658879a71152ea075c74154a627d05
- https://access.redhat.com/security/cve/CVE-2025-62400
- https://bugzilla.redhat.com/show_bug.cgi?id=2404433
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=470389
