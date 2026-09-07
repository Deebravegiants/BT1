# [M] Moodle Improper Input Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-gv8f-43pg-c5qw
CVE: CVE-2021-36402
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-03-07
Source: https://github.com/advisories/GHSA-gv8f-43pg-c5qw
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.11.0-beta <3.11.1
- Packagist: `moodle/moodle` — affected >=3.10.0-beta <3.10.5
- Packagist: `moodle/moodle` — affected >=0 <3.9.8

## Details
In affected versions of Moodle, users' names require additional sanitizing in the account confirmation email, to prevent a self-registration phishing risk. This issue has been patched in versions 3.9.8, 3.10.5 and 3.11.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36402
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=424808
