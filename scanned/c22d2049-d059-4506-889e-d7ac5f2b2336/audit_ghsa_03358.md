# [H] Improper Input Validation in klona

## Summary
Severity: High
Advisory: GHSA-8f89-2fwj-5v5r
CVE: CVE-2020-8125
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-8f89-2fwj-5v5r
Type: github-advisory

## Affected
- npm: `klona` — affected >=0 <1.1.1

## Details
Flaw in input validation in npm package klona version 1.1.0 and earlier may allow prototype pollution attack that may result in remote code execution or denial of service of applications using klona.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8125
- https://github.com/lukeed/klona/commit/200e8d1fd383a54790ee6fc8228264c21954e38e
- https://hackerone.com/reports/778414
