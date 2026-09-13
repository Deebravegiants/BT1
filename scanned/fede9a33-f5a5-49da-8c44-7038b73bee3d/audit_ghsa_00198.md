# [C] Command Injection in whereis

## Summary
Severity: Critical
Advisory: GHSA-wjr4-2jgw-hmv8
CVE: CVE-2018-3772
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-31
Source: https://github.com/advisories/GHSA-wjr4-2jgw-hmv8
Type: github-advisory

## Affected
- npm: `whereis` — affected >=0 <0.4.1

## Details
Versions of `whereis` before 0.4.1 are vulnerable to command injection if untrusted user input is passed into `whereis`.


## Recommendation

Update to version 0.4.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3772
- https://github.com/vvo/node-whereis/commit/0f64e3780235004fb6e43bfd153ea3e0e210ee2b
- https://hackerone.com/reports/319476
- https://github.com/advisories/GHSA-wjr4-2jgw-hmv8
- https://www.npmjs.com/advisories/604
