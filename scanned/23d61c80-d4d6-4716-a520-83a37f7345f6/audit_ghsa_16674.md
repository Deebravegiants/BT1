# [M] Moodle broken access control when setting calendar event type

## Summary
Severity: Medium
Advisory: GHSA-4qww-rxq6-x7gf
CVE: CVE-2024-33996
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2024-05-31
Source: https://github.com/advisories/GHSA-4qww-rxq6-x7gf
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.3.0 <4.3.4
- Packagist: `moodle/moodle` — affected >=4.2.0 <4.2.7
- Packagist: `moodle/moodle` — affected >=0 <4.1.10

## Details
Incorrect validation of allowed event types in a calendar web service made it possible for some users to create events with types/audiences they did not have permission to publish to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-33996
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=458384#p1840909
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-81247
