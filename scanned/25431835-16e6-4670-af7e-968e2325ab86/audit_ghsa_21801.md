# [C] OS Command Injection in jscover

## Summary
Severity: Critical
Advisory: GHSA-c5hm-xc74-pqrg
CVE: CVE-2020-7623
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-c5hm-xc74-pqrg
Type: github-advisory

## Affected
- npm: `jscover` — affected >=0

## Details
jscover through 1.0.0 is vulnerable to Command Injection. It allows execution of arbitrary command via the source argument.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7623
- https://github.com/node-modules/jscover/blob/master/lib/jscover.js#L59
- https://snyk.io/vuln/SNYK-JS-JSCOVER-564250
