# [M] czim/file-handling vulnerable to SSRF and directory traversal

## Summary
Severity: Medium
Advisory: GHSA-6rgh-r6j3-3223
CVE: CVE-2024-47049
CWE: CWE-22, CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-6rgh-r6j3-3223
Type: github-advisory

## Affected
- Packagist: `czim/file-handling` — affected >=0 <1.5.0
- Packagist: `czim/file-handling` — affected >=2.0.0 <2.3.0

## Details
The czim/file-handling package before 1.5.0 and 2.x before 2.3.0 (used with PHP Composer) does not properly validate URLs within makeFromUrl and makeFromAny, leading to SSRF, and to directory traversal for the reading of local files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-47049
- https://github.com/czim/file-handling/commit/95dfda850536bf35e684619598b9d02f4c97680d
- https://github.com/czim/file-handling/commit/dcf879896efe3457f51af9c8eab9f70dfc709a99
- https://github.com/czim/file-handling
- https://github.com/czim/file-handling/blob/2.3.0/SECURITY.md
