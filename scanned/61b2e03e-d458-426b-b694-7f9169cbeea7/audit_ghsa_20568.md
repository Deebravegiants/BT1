# [C] SQL injection in Moodle

## Summary
Severity: Critical
Advisory: GHSA-6jhm-4vmx-mr76
CVE: CVE-2022-0332
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-28
Source: https://github.com/advisories/GHSA-6jhm-4vmx-mr76
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.11 <3.11.5

## Details
A flaw was found in Moodle in versions 3.11 to 3.11.4. An SQL injection risk was identified in the h5p activity web service responsible for fetching user attempt data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0332
- https://github.com/moodle/moodle/commit/c7a62a8c82219b50589257f79021da1df1a76808
- https://bugzilla.redhat.com/show_bug.cgi?id=2043661
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=431099
