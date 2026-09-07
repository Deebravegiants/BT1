# [H] Moodle Arbitrary PHP code execution by site admins via Shibboleth configuration

## Summary
Severity: High
Advisory: GHSA-2jrm-gww7-wch2
CVE: CVE-2021-20187
CWE: CWE-829, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2jrm-gww7-wch2
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.5 <3.5.16
- Packagist: `moodle/moodle` — affected >=3.8 <3.8.7
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.4
- Packagist: `moodle/moodle` — affected >=3.10 <3.10.1

## Details
It was found in Moodle before version 3.10.1, 3.9.4, 3.8.7 and 3.5.16 that it was possible for site administrators to execute arbitrary PHP scripts via a PHP include used during Shibboleth authentication.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20187
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=417171
