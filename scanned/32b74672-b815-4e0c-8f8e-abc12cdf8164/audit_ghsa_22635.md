# [M] Path Traversal in FileGator

## Summary
Severity: Medium
Advisory: GHSA-rrhw-54r8-545q
CVE: CVE-2022-1850
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-rrhw-54r8-545q
Type: github-advisory

## Affected
- Packagist: `filegator/filegator` — affected >=0 <7.8.0

## Details
Path Traversal in FileGator prior to 7.8.0 for non-admin users. Files created with `..\` as part of their name will be interpreted as a path. Users are thus able to add filesystem entries outside the scope of their user to their dashboard and subsequently are able to modify those files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1850
- https://github.com/filegator/filegator/commit/6e2b68f17f48cdc1d6a4a93a2369d2069fe64989
- https://github.com/filegator/filegator
- https://huntr.dev/bounties/07755f07-a412-4911-84a4-2f8c03c8f7ce
