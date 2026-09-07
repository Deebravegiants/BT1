# [C] Code Injection in cd-messenger

## Summary
Severity: Critical
Advisory: GHSA-v756-4whv-48vc
CVE: CVE-2020-7675
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-17
Source: https://github.com/advisories/GHSA-v756-4whv-48vc
Type: github-advisory

## Affected
- npm: `cd-messenger` — affected >=0

## Details
cd-messenger through 2.7.26 is vulnerable to Arbitrary Code Execution. User input provided to the `color` argument executed by the `eval` function resulting in code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7675
- https://snyk.io/vuln/SNYK-JS-CDMESSENGER-571493
