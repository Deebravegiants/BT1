# [M] BookStack is vulnerable to Improper Access Control.

## Summary
Severity: Medium
Advisory: GHSA-9c5c-5j4h-8q2c
CVE: CVE-2021-4119
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-12-16
Source: https://github.com/advisories/GHSA-9c5c-5j4h-8q2c
Type: github-advisory

## Affected
- Packagist: `ssddanbrown/bookstack` — affected >=0 <21.11.3

## Details
BookStack prior to version 21.11.3 is vulnerable to Improper Access Control. A logged-in user with no privileges OR guest user (if public access enabled) can access the /search/users/select AJAX endpoint meant for admins to manage audit logs, to dump all usernames existing in the Bookstack database. This can also be used to harvest email belonging to a user because BookStack also uses the code where(`email`, `like`, `%` . $search . `%`) to search for users based on email.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4119
- https://github.com/bookstackapp/bookstack/commit/e765e618547c92f4e0b46caca6fb91f0174efd99
- https://github.com/BookStackApp/BookStack/releases/tag/v21.11.3
- https://github.com/bookstackapp/bookstack
- https://huntr.dev/bounties/135f2d7d-ab0b-4351-99b9-889efac46fca
