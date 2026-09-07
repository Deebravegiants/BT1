# [M] Moodle does not revoke role capabilities correctly

## Summary
Severity: Medium
Advisory: GHSA-g9m2-c2x5-fr2v
CVE: CVE-2019-14879
CWE: CWE-273
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-g9m2-c2x5-fr2v
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.7.0 <3.7.3
- Packagist: `moodle/moodle` — affected >=3.6.0 <3.6.7
- Packagist: `moodle/moodle` — affected >=3.5.0 <3.5.9

## Details
A vulnerability was found in Moodle versions 3.7.x before 3.7.3, 3.6.x before 3.6.7 and 3.5.x before 3.5.9. When a cohort role assignment was removed, the associated capabilities were not being revoked (where applicable).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14879
- https://github.com/moodle/moodle/commit/7b5f4a62c18fd5bad6956828aade23e1f15b4be3
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14879
