# [M] Moodle Inserts Sensitive Information Into Sent Data

## Summary
Severity: Medium
Advisory: GHSA-8jrv-wx83-w3xj
CVE: CVE-2025-67857
CWE: CWE-201
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-8jrv-wx83-w3xj
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.22
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.12
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.8
- Packagist: `moodle/moodle` — affected >=5.0.0-beta <5.0.4
- Packagist: `moodle/moodle` — affected >=5.1.0-beta <5.1.1

## Details
A flaw was found in moodle. During anonymous assignment submissions, user identifiers were inadvertently exposed in URLs. This data exposure allows unauthorized viewers to see internal user IDs, compromising the intended anonymity and potentially leading to information disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67857
- https://github.com/moodle/moodle/commit/ac30e7e19357f696979b7ffd760a7131b6ad88f6
- https://github.com/moodle/moodle/commit/c6cb8d971257c04a12a2c5d8510a89cb906f46f0
- https://access.redhat.com/security/cve/CVE-2025-67857
- https://bugzilla.redhat.com/show_bug.cgi?id=2423868
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=471307
