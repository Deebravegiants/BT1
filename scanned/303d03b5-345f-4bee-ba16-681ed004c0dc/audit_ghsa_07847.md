# [H] Moodle Affected by Improper Restriction of Excessive Authentication Attempts

## Summary
Severity: High
Advisory: GHSA-5cx4-w4fh-fr57
CVE: CVE-2025-67853
CWE: CWE-307
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-5cx4-w4fh-fr57
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.22
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.12
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.8
- Packagist: `moodle/moodle` — affected >=5.0.0-beta <5.0.4
- Packagist: `moodle/moodle` — affected >=5.1.0-beta <5.1.1

## Details
A flaw was found in Moodle. A remote attacker could exploit a lack of proper rate limiting in the confirmation email service. This vulnerability allows attackers to more easily enumerate or guess user credentials, facilitating brute-force attacks against user accounts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67853
- https://access.redhat.com/security/cve/CVE-2025-67853
- https://bugzilla.redhat.com/show_bug.cgi?id=2423847
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=471303
