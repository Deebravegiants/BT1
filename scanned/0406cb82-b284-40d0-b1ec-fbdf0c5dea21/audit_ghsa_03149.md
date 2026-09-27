# [C] OS Command Injection in pomelo-monitor

## Summary
Severity: Critical
Advisory: GHSA-4j54-mxf6-wxx2
CVE: CVE-2020-7620
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-4j54-mxf6-wxx2
Type: github-advisory

## Affected
- npm: `pomelo-monitor` — affected >=0

## Details
pomelo-monitor through 0.3.7 is vulnerable to Command Injection.It allows injection of arbitrary commands as part of 'pomelo-monitor' params.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7620
- https://github.com/halfblood369/monitor/blob/900b5cadf59edcccac4754e5706a22719925ddb9/lib/processMonitor.js,
- https://snyk.io/vuln/SNYK-JS-POMELOMONITOR-173695
