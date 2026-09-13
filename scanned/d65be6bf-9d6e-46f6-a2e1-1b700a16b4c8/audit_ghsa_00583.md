# [H] Insufficient Error Handling in http-proxy

## Summary
Severity: High
Advisory: GHSA-9xw9-pvgv-6p76
CVE: CVE-2017-16014
CWE: CWE-703
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-9xw9-pvgv-6p76
Type: github-advisory

## Affected
- npm: `http-proxy` — affected >=0 <0.7.0

## Details
Affected versions of `http-proxy` are vulnerable to a denial of service attack, wherein an attacker can force an error which will cause the server to crash.


## Recommendation

Update to version 0.7.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16014
- https://github.com/nodejitsu/node-http-proxy/pull/101
- https://github.com/advisories/GHSA-9xw9-pvgv-6p76
- https://www.npmjs.com/advisories/323
