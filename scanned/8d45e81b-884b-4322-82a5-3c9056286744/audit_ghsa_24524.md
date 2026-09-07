# [M] Moodle External blog editing takeover

## Summary
Severity: Medium
Advisory: GHSA-m34m-fgh4-v7cx
CVE: CVE-2017-7489
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-m34m-fgh4-v7cx
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.2 <3.2.3
- Packagist: `moodle/moodle` — affected >=3.1 <3.1.6
- Packagist: `moodle/moodle` — affected >=3.0 <3.0.10
- Packagist: `moodle/moodle` — affected >=2.7 <2.7.20

## Details
In Moodle 2.x and 3.x, remote authenticated users can take ownership of arbitrary blogs by editing an external blog link.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7489
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=352353
