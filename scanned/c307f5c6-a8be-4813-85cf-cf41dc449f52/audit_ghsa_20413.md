# [H] Exposure of Sensitive Information in simple-get

## Summary
Severity: High
Advisory: GHSA-wpg7-2c88-r8xv
CVE: CVE-2022-0355
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-28
Source: https://github.com/advisories/GHSA-wpg7-2c88-r8xv
Type: github-advisory

## Affected
- npm: `simple-get` — affected >=4.0.0 <4.0.1
- npm: `simple-get` — affected >=3.0.0 <3.1.1
- npm: `simple-get` — affected >=0 <2.8.2

## Details
In versions of simple-get prior to 4.0.1, 3.1.1, and 2.8.2, when fetching a remote url with a cookie location response, headers will be followed, potentially resulting in an exposure of the session cookie to a third party.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0355
- https://github.com/feross/simple-get/pull/75#issuecomment-1027755026
- https://github.com/feross/simple-get/pull/76#issuecomment-1027754710
- https://github.com/feross/simple-get/commit/e4af095e06cd69a9235013e8507e220a79b9684f
- https://github.com/feross/simple-get
- https://huntr.dev/bounties/42c79c23-6646-46c4-871d-219c0d4b4e31
