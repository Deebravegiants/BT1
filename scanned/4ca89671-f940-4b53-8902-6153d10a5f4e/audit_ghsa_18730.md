# [M] Moodle's error handling leads to sensitive information disclosure

## Summary
Severity: Medium
Advisory: GHSA-c5cj-xp43-qcc3
CVE: CVE-2025-62396
CWE: CWE-548
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-10-23
Source: https://github.com/advisories/GHSA-c5cj-xp43-qcc3
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=5.0.0-beta <5.0.3
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.7

## Details
An error-handling issue in the Moodle router (r.php) could cause the application to display internal directory listings when specific HTTP headers were not properly configured.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62396
- https://github.com/moodle/moodle/commit/5d4910509eeaac8403d18ec8f259e29d2f11527e
- https://github.com/moodle/moodle/commit/5e7d5abc483d0511ebfc2042075eabcc392ff4ce
- https://access.redhat.com/security/cve/CVE-2025-62396
- https://bugzilla.redhat.com/show_bug.cgi?id=2404429
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=470385
