# [H] ReDoS in normalize-url

## Summary
Severity: High
Advisory: GHSA-px4h-xg32-q955
CVE: CVE-2021-33502
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-px4h-xg32-q955
Type: github-advisory

## Affected
- npm: `normalize-url` — affected >=4.3.0 <4.5.1
- npm: `normalize-url` — affected >=5.0.0 <5.3.1
- npm: `normalize-url` — affected >=6.0.0 <6.0.1

## Details
The normalize-url package before 4.5.1, 5.x before 5.3.1, and 6.x before 6.0.1 for Node.js has a ReDoS (regular expression denial of service) issue because it has exponential performance for data: URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33502
- https://github.com/sindresorhus/normalize-url/commit/b1fdb5120b6d27a88400d8800e67ff5a22bd2103
- https://github.com/sindresorhus/normalize-url
- https://github.com/sindresorhus/normalize-url/releases/tag/v6.0.1
- https://security.netapp.com/advisory/ntap-20210706-0001
