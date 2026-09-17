# [M] Path Traversal in angular-http-server

## Summary
Severity: Medium
Advisory: GHSA-4rvg-955w-h68q
CVE: CVE-2018-3713
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-26
Source: https://github.com/advisories/GHSA-4rvg-955w-h68q
Type: github-advisory

## Affected
- npm: `angular-http-server` — affected >=0 <1.6.0

## Details
Affected versions of `angular-http-server` are vulnerable to path traversal allowing a remote attacker to read files from the server that uses `angular-http-server`.

## Recommendation

Update to version 1.6.0 or later.

:exclamation: Note: This was originally thought to be fixed in version 1.4.3, though according to [this issue](https://github.com/ossf-cve-benchmark/ossf-cve-benchmark/issues/117#issuecomment-803872454) the vulnerability was not completely fixed until version 1.6.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3713
- https://github.com/simonh1000/angular-http-server/pull/21
- https://github.com/simonh1000/angular-http-server/commit/34d4bd0cd0f00c46db30855a8c4aabae27eb0ac8
- https://hackerone.com/reports/309120
- https://github.com/advisories/GHSA-4rvg-955w-h68q
- https://www.npmjs.com/advisories/589
