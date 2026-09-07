# [H] Moodle incorrect access control

## Summary
Severity: High
Advisory: GHSA-f5r8-7h4f-jr9x
CVE: CVE-2020-25629
CWE: CWE-284, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f5r8-7h4f-jr9x
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.2
- Packagist: `moodle/moodle` — affected >=3.8 <3.8.5
- Packagist: `moodle/moodle` — affected >=3.7 <3.7.8
- Packagist: `moodle/moodle` — affected >=3.5 <3.5.14

## Details
A vulnerability was found in Moodle where users with "Log in as" capability in a course context (typically, course managers) may gain access to some site administration capabilities by "logging in as" a System manager. This affects 3.9 to 3.9.1, 3.8 to 3.8.4, 3.7 to 3.7.7, 3.5 to 3.5.13 and earlier unsupported versions. This is fixed in 3.9.2, 3.8.5, 3.7.8 and 3.5.14.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25629
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=410841
