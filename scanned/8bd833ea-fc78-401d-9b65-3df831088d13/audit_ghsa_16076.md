# [M] Moodle IDOR when accessing list of course badges

## Summary
Severity: Medium
Advisory: GHSA-r4xr-m393-778m
CVE: CVE-2024-48899
CWE: CWE-284, CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-11-20
Source: https://github.com/advisories/GHSA-r4xr-m393-778m
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.3

## Details
A vulnerability was found in Moodle. Additional checks are required to ensure users can only fetch the list of course badges for courses that they are intended to have access to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48899
- https://github.com/moodle/moodle/commit/07ad4b8ebc715056056e01f2175820bfce6b290f
- https://bugzilla.redhat.com/show_bug.cgi?id=2318819
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=462878#p1858337
