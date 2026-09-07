# [M] Moodle does not properly enforce MFA

## Summary
Severity: Medium
Advisory: GHSA-25wf-7x6c-wmpf
CVE: CVE-2025-62398
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-10-23
Source: https://github.com/advisories/GHSA-25wf-7x6c-wmpf
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=5.0.0-beta <5.0.3
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.7
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.11

## Details
A serious authentication flaw allowed attackers with valid credentials to bypass multi-factor authentication under certain conditions, potentially compromising user accounts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62398
- https://github.com/moodle/moodle/commit/67005f8b2098096f4c7ca4f78ab9ce69415d703b
- https://github.com/moodle/moodle/commit/a2078f781ae065ca1f781bd159c7615c84afcaa5
- https://access.redhat.com/security/cve/CVE-2025-62398
- https://bugzilla.redhat.com/show_bug.cgi?id=2404431
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=470387
