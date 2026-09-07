# [H] Moodle vulnerable to brute-force password guesses

## Summary
Severity: High
Advisory: GHSA-m58f-9pvv-8mp2
CVE: CVE-2025-62399
CWE: CWE-307
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-10-23
Source: https://github.com/advisories/GHSA-m58f-9pvv-8mp2
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=5.0.0-beta <5.0.3
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.7
- Packagist: `moodle/moodle` — affected >=4.2.0-beta <4.4.11
- Packagist: `moodle/moodle` — affected >=0 <4.1.21

## Details
Moodle's mobile and web service authentication endpoints did not sufficiently restrict repeated password attempts, making them susceptible to brute-force attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62399
- https://github.com/moodle/moodle/commit/e4d02567c922c537086de9f59f063ca073552a3a
- https://access.redhat.com/security/cve/CVE-2025-62399
- https://bugzilla.redhat.com/show_bug.cgi?id=2404432
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=470388
