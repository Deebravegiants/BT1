# [H] Moodle contains CSRF vulnerability

## Summary
Severity: High
Advisory: GHSA-3jrj-x6cj-97cp
CVE: CVE-2021-43559
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3jrj-x6cj-97cp
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.11 <3.11.4
- Packagist: `moodle/moodle` — affected >=3.10 <3.10.8
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.11

## Details
A flaw was found in Moodle in versions 3.11 to 3.11.3, 3.10 to 3.10.7, 3.9 to 3.9.10 and earlier unsupported versions. The "delete related badge" functionality did not include the necessary token check to prevent a CSRF risk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43559
- https://github.com/moodle/moodle/commit/20d41ebae4eb28269298504c68db511a05ec4969
- https://bugzilla.redhat.com/show_bug.cgi?id=2021517
- https://moodle.org/mod/forum/discuss.php?d=429099
