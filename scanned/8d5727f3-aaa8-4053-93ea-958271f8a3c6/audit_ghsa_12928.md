# [H] MooTools Regular Expression Denial of Service

## Summary
Severity: High
Advisory: GHSA-v63q-hgqc-qvpg
CVE: CVE-2021-32821
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-01-03
Source: https://github.com/advisories/GHSA-v63q-hgqc-qvpg
Type: github-advisory

## Affected
- npm: `mootools` — affected >=0

## Details
MooTools is a collection of JavaScript utilities for JavaScript developers. All known versions include a CSS selector parser that is vulnerable to Regular Expression Denial of Service (ReDoS). An attack requires that an attacker can inject a string into a CSS selector at runtime, which is quite common with e.g. jQuery CSS selectors. No patches are available for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32821
- https://github.com/vsviridov/mootools-node
- https://securitylab.github.com/advisories/GHSL-2020-345-redos-mootools
