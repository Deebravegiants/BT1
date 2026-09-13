# [H] Mongoose search injection vulnerability

## Summary
Severity: High
Advisory: GHSA-m7xq-9374-9rvx
CVE: CVE-2024-53900
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-m7xq-9374-9rvx
Type: github-advisory

## Affected
- npm: `mongoose` — affected >=8.0.0-rc0 <8.8.3
- npm: `mongoose` — affected >=7.0.0-rc0 <7.8.3
- npm: `mongoose` — affected >=6.0.0-rc0 <6.13.5
- npm: `mongoose` — affected >=3.6.0-rc0 <5.13.23

## Details
Mongoose versions prior to 8.8.3, 7.8.3, 6.13.5, and 5.13.23 are vulnerable to improper use of the $where operator. This vulnerability arises from the ability of the $where clause to execute arbitrary JavaScript code in MongoDB queries, potentially leading to code injection attacks and unauthorized access or manipulation of database data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-53900
- https://github.com/github/advisory-database/pull/6769
- https://github.com/github/advisory-database/pull/6776
- https://github.com/Automattic/mongoose/commit/33679bcf8ca43d74e3e8ecd4cc224826772d805b
- https://github.com/Automattic/mongoose/commit/bbb6fa7ecb44bbaf5bea955d886378a1247bce0b
- https://github.com/Automattic/mongoose/commit/c9e86bff7eef477da75a29af62a06d41a835a156
- https://github.com/Automattic/mongoose
- https://github.com/Automattic/mongoose/blob/master/CHANGELOG.md
- https://github.com/Automattic/mongoose/compare/6.13.4...6.13.5
- https://github.com/Automattic/mongoose/compare/7.8.2...7.8.3
- https://github.com/Automattic/mongoose/compare/8.8.2...8.8.3
- https://github.com/Automattic/mongoose/releases
- https://www.npmjs.com/package/mongoose?activeTab=versions
