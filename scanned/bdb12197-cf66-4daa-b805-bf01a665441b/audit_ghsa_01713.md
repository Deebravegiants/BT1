# [C] OS Command Injection in devcert-sanscache

## Summary
Severity: Critical
Advisory: GHSA-4gp3-p7ph-x2jr
CVE: CVE-2019-10778
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-04-14
Source: https://github.com/advisories/GHSA-4gp3-p7ph-x2jr
Type: github-advisory

## Affected
- npm: `devcert-sanscache` — affected >=0 <0.4.7

## Details
devcert-sanscache before 0.4.7 allows remote attackers to execute arbitrary code or cause a Command Injection via the exec function. The variable `commonName` controlled by user input is used as part of the `exec` function without any sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10778
- https://github.com/guybedford/devcert/commit/571f4e6d077f7f21c6aed655ae380d85a7a5d3b8
- https://snyk.io/vuln/SNYK-JS-DEVCERTSANSCACHE-540926
