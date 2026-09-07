# [M] Moodle Improper Encoding or Escaping of Output

## Summary
Severity: Medium
Advisory: GHSA-m37g-mwcg-7j7v
CVE: CVE-2021-40694
CWE: CWE-116
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-30
Source: https://github.com/advisories/GHSA-m37g-mwcg-7j7v
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.10
- Packagist: `moodle/moodle` — affected >=3.10 <3.10.7
- Packagist: `moodle/moodle` — affected >=3.11 <3.11.3

## Details
Insufficient escaping of the LaTeX preamble made it possible for site administrators to read files available to the HTTP server system account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40694
- https://bugzilla.redhat.com/show_bug.cgi?id=2043421
- https://github.com/moodle/moodle
