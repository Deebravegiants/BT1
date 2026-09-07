# [M] Moodle leaks user names

## Summary
Severity: Medium
Advisory: GHSA-cq5f-wv7p-5gfc
CVE: CVE-2024-48896
CWE: CWE-209
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-11-18
Source: https://github.com/advisories/GHSA-cq5f-wv7p-5gfc
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.14
- Packagist: `moodle/moodle` — affected >=4.2.0 <4.2.11
- Packagist: `moodle/moodle` — affected >=4.3.0 <4.3.8
- Packagist: `moodle/moodle` — affected >=4.4.0 <4.4.4

## Details
A vulnerability was found in Moodle. It is possible for users with the "send message" capability to view other users' names that they may not otherwise have access to via an error message in Messaging. Note: The name returned follows the full name format configured on the site.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48896
- https://bugzilla.redhat.com/show_bug.cgi?id=2318822
- https://github.com/moodle/moodle
