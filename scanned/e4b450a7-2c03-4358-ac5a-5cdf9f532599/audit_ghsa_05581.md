# [H] Moodle affected by a code injection vulnerability

## Summary
Severity: High
Advisory: GHSA-xvmh-25jw-gmmm
CVE: CVE-2025-67847
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-23
Source: https://github.com/advisories/GHSA-xvmh-25jw-gmmm
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=5.1.0-beta <5.1.1
- Packagist: `moodle/moodle` — affected >=5.0.0-beta <5.0.4
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.8
- Packagist: `moodle/moodle` — affected >=4.2.0-beta <4.4.12
- Packagist: `moodle/moodle` — affected >=0 <4.1.22

## Details
A flaw was found in Moodle. An attacker with access to the restore interface could trigger server-side execution of arbitrary code. This is due to insufficient validation of restore input, which leads to unintended interpretation by core restore routines. Successful exploitation could result in a full compromise of the Moodle application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67847
- https://access.redhat.com/security/cve/CVE-2025-67847
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=471297#p1892199
