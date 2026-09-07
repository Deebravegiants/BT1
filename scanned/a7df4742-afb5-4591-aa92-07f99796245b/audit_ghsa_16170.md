# [M] Moodle IDOR when deleting OAuth2 linked accounts

## Summary
Severity: Medium
Advisory: GHSA-fhg2-r2h9-h7q8
CVE: CVE-2024-45690
CWE: CWE-276, CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-11-20
Source: https://github.com/advisories/GHSA-fhg2-r2h9-h7q8
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.13
- Packagist: `moodle/moodle` — affected >=4.2.0-beta <4.2.10
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.7
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.3

## Details
A flaw was found in Moodle. Additional checks were required to ensure users can only delete their OAuth2-linked accounts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45690
- https://github.com/moodle/moodle/commit/809629e5afcd5be087e65668fe6cf67f2f4f5145
- https://bugzilla.redhat.com/show_bug.cgi?id=2309939
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=461895#p1854492
- https://moodle.org/security
