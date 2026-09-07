# [C] karma-mojo enables OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-pf8j-vhg8-xmc3
CVE: CVE-2020-7626
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-pf8j-vhg8-xmc3
Type: github-advisory

## Affected
- npm: `karma-mojo` — affected >=0

## Details
karma-mojo through 1.0.1 is vulnerable to Command Injection. It allows execution of arbitrary commands via the config argument.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7626
- https://github.com/amireh/karma-mojo/blob/master/index.js#L100
- https://snyk.io/vuln/SNYK-JS-KARMAMOJO-564260
