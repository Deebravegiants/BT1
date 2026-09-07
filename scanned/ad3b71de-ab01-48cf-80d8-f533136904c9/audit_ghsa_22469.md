# [M] Moodle Email media URL tokens were not checking for user status

## Summary
Severity: Medium
Advisory: GHSA-774q-wfcp-vc2q
CVE: CVE-2019-14883
CWE: CWE-285, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-774q-wfcp-vc2q
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.6 <3.6.7
- Packagist: `moodle/moodle` — affected >=3.7 <3.7.3

## Details
A vulnerability was found in Moodle 3.6 before 3.6.7 and 3.7 before 3.7.3, where tokens used to fetch inline atachments in email notifications were not disabled when a user's account was no longer active. Note: to access files, a user would need to know the file path, and their token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14883
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14883
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=393586#p1586750
