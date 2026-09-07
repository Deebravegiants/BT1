# [M] Moodle No groups filtering in H5P activity attempts report

## Summary
Severity: Medium
Advisory: GHSA-385f-vgq7-8hhx
CVE: CVE-2022-40316
CWE: CWE-668, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-10-01
Source: https://github.com/advisories/GHSA-385f-vgq7-8hhx
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.17
- Packagist: `moodle/moodle` — affected >=3.11 <3.11.10
- Packagist: `moodle/moodle` — affected >=4.0 <4.0.4

## Details
The H5P activity attempts report did not filter by groups, which in separate groups mode could reveal information to non-editing teachers about attempts/users in groups they should not have access to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40316
- https://bugzilla.redhat.com/show_bug.cgi?id=2128151
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=438395
