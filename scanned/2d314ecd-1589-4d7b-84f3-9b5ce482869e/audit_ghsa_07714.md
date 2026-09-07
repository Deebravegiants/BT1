# [H] Moodle authentication bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-j5jv-w5cw-j9ff
CVE: CVE-2025-67848
CWE: CWE-280
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-j5jv-w5cw-j9ff
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.22
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.12
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.8
- Packagist: `moodle/moodle` — affected >=5.0.0-beta <5.0.4
- Packagist: `moodle/moodle` — affected >=5.1.0-beta <5.1.1

## Details
A flaw was found in Moodle. This authentication bypass vulnerability allows suspended users to authenticate through the Learning Tools Interoperability (LTI) Provider. The issue arises from the LTI authentication handlers failing to enforce the user's suspension status, enabling unauthorized access to the system. This can lead to information disclosure or other unauthorized actions by users who should be restricted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67848
- https://github.com/moodle/moodle/commit/62f372e9d861d16df702d3c7726905fa2730e3d8
- https://github.com/moodle/moodle/commit/c2705e2c18962fec4f21b9c34ed386be2a379663
- https://access.redhat.com/security/cve/CVE-2025-67848
- https://bugzilla.redhat.com/show_bug.cgi?id=2423831
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=471298
