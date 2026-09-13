# [H] thorsten/phpmyfaq vulnerable privilege escalation from improper privilege management 

## Summary
Severity: High
Advisory: GHSA-xww4-w6ff-5q3g
CVE: CVE-2023-1762
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-31
Source: https://github.com/advisories/GHSA-xww4-w6ff-5q3g
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <3.1.12

## Details
thorsten/phpmyfaq prior to 3.1.12 is vulnerable to privilege escalation from improper privilege management. Any user with the ability to add a new user can create a user with super admin rights. This has been fixed in 3.1.12.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1762
- https://github.com/thorsten/phpmyfaq/commit/ae6c1d8c3eab05d6e2227c7a9998707f4f891514
- https://github.com/thorsten/phpmyfaq
- https://huntr.dev/bounties/3c2374cc-7082-44b7-a6a6-ccff7a650a3a
