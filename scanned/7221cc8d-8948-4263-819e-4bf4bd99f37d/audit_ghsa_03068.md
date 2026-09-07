# [C] Improper Input Validation in access-policy

## Summary
Severity: Critical
Advisory: GHSA-fw2f-7f87-5r6c
CVE: CVE-2020-7674
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-17
Source: https://github.com/advisories/GHSA-fw2f-7f87-5r6c
Type: github-advisory

## Affected
- npm: `access-policy` — affected >=0

## Details
access-policy through 3.1.0 is vulnerable to Arbitrary Code Execution. User input provided to the `template` function is executed by the `eval` function resulting in code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7674
- https://snyk.io/vuln/SNYK-JS-ACCESSPOLICY-571490
