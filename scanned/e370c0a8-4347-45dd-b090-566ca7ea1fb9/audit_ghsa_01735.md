# [M] XSS in knockout

## Summary
Severity: Medium
Advisory: GHSA-vcjj-xf2r-mwvc
CVE: CVE-2019-14862
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-04-01
Source: https://github.com/advisories/GHSA-vcjj-xf2r-mwvc
Type: github-advisory

## Affected
- npm: `knockout` — affected >=0 <3.5.0

## Details
There is a vulnerability in knockout before version 3.5.0-beta, where after escaping the context of the web application, the web application delivers data to its users along with other trusted dynamic content, without validating it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14862
- https://github.com/knockout/knockout/issues/1244
- https://github.com/knockout/knockout/pull/2345
- https://github.com/knockout/knockout/commit/7e280b2b8a04cc19176b5171263a5c68bda98efb
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14862
- https://snyk.io/vuln/npm:knockout:20180213
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.whitesourcesoftware.com/vulnerability-database/WS-2019-0015
