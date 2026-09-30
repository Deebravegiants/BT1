# [H] BookStack Incorrect Access Control vulnerability

## Summary
Severity: High
Advisory: GHSA-pj36-fcrg-327j
CVE: CVE-2024-36676
CWE: CWE-284, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2024-07-10
Source: https://github.com/advisories/GHSA-pj36-fcrg-327j
Type: github-advisory

## Affected
- Packagist: `ssddanbrown/bookstack` — affected >=0 <24.05.1

## Details
Incorrect access control in BookStack before v24.05.1 allows attackers to confirm existing system users and perform targeted notification email DoS via public facing forms.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36676
- https://github.com/BookStackApp/BookStack/issues/4993
- https://github.com/BookStackApp/BookStack/commit/69af9e0dbdefd8c6c951e8afbe2bba141d454beb
- https://github.com/BookStackApp/BookStack
- https://github.com/BookStackApp/BookStack/releases/tag/v24.05.1
- https://www.bookstackapp.com/blog/bookstack-release-v24-05-1
