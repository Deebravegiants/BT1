# [M] moodle: Some users can delete audiences of other reports

## Summary
Severity: Medium
Advisory: GHSA-fjq9-452g-jg3q
CVE: CVE-2024-48898
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-11-18
Source: https://github.com/advisories/GHSA-fjq9-452g-jg3q
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.14
- Packagist: `moodle/moodle` — affected >=4.2.0 <4.2.11
- Packagist: `moodle/moodle` — affected >=4.3.0 <4.3.8
- Packagist: `moodle/moodle` — affected >=4.4.0 <4.4.4

## Details
A vulnerability was found in Moodle. Users with access to delete audiences from reports could delete audiences from other reports that they do not have permission to delete from.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48898
- https://bugzilla.redhat.com/show_bug.cgi?id=2318820
- https://github.com/moodle/moodle
