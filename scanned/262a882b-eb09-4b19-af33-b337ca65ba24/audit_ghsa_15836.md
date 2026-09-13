# [M] validate.js Regular Expression Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rv73-9c8w-jp4c
CVE: CVE-2020-26308
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U/U:Green (CVSS_V4)
Published: 2024-10-26
Source: https://github.com/advisories/GHSA-rv73-9c8w-jp4c
Type: github-advisory

## Affected
- npm: `validate.js` — affected >=0

## Details
Validate.js provides a declarative way of validating javascript objects. Versions 0.13.1 and prior contain one or more regular expressions that are vulnerable to Regular Expression Denial of Service (ReDoS). As of time of publication, no known patches are available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26308
- https://github.com/ansman/validate.js/issues/342
- https://github.com/ansman/validate.js
- https://securitylab.github.com/advisories/GHSL-2020-302-redos-validate.js
