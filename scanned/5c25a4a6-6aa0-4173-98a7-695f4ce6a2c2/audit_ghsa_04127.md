# [H] Regular Expression Denial of Service in highcharts

## Summary
Severity: High
Advisory: GHSA-xmc8-cjfr-phx3
CVE: CVE-2018-20801
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-03-18
Source: https://github.com/advisories/GHSA-xmc8-cjfr-phx3
Type: github-advisory

## Affected
- npm: `highcharts` — affected >=0 <6.1.0

## Details
Versions of `highcharts` prior to 6.1.0 are vulnerable to Regular Expression Denial of Service (ReDoS). Untrusted input may cause catastrophic backtracking while matching regular expressions. This can cause the application to be unresponsive leading to Denial of Service.


## Recommendation

Upgrade to version 6.1.0 or higher.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20801
- https://github.com/highcharts/highcharts/commit/7c547e1e0f5e4379f94396efd559a566668c0dfa
- https://github.com/advisories/GHSA-xmc8-cjfr-phx3
- https://github.com/highcharts/highcharts
- https://security.netapp.com/advisory/ntap-20190715-0001
- https://snyk.io/vuln/npm:highcharts:20180225
- https://www.npmjs.com/advisories/793
