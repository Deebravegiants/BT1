# [C] Arbitrary Command Injection

## Summary
Severity: Critical
Advisory: GHSA-v85c-hgq5-7pfw
CVE: CVE-2021-23399
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-29
Source: https://github.com/advisories/GHSA-v85c-hgq5-7pfw
Type: github-advisory

## Affected
- npm: `wincred` — affected >=0

## Details
This affects all versions of package wincred. If attacker-controlled user input is given to the getCredential function, it is possible for an attacker to execute arbitrary commands. This is due to use of the child_process exec function without input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23399
- https://github.com/rolangom/wincred/blob/3fd39186ee32add9c12046cdccf2765d19565335/index.ts%23L20
- https://snyk.io/vuln/SNYK-JS-WINCRED-1078538
