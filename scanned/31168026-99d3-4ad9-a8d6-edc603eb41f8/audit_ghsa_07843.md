# [M] Moodle formula injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qfh6-h7j6-fvjv
CVE: CVE-2025-67851
CWE: CWE-1236
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-qfh6-h7j6-fvjv
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.22
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.12
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.8
- Packagist: `moodle/moodle` — affected >=5.0.0-beta <5.0.4
- Packagist: `moodle/moodle` — affected >=5.1.0-beta <5.1.1

## Details
A flaw was found in Moodle. This formula injection vulnerability occurs when data fields are exported without proper escaping. A remote attacker could exploit this by providing malicious data that, when exported and opened in a spreadsheet, allows arbitrary formulas to execute. This can lead to compromised data integrity and unintended operations within the spreadsheet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67851
- https://github.com/moodle/moodle/commit/29820c5ff4ef381c7a743091ec5c68ac82903b22
- https://github.com/moodle/moodle/commit/aa66bacd0783cbc33528fba9c2adca1f685a59bd
- https://github.com/moodle/moodle/commit/dc57ccc491a2a04032445a3ee92fd0d335ebd746
- https://access.redhat.com/security/cve/CVE-2025-67851
- https://bugzilla.redhat.com/show_bug.cgi?id=2423841
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=471301
