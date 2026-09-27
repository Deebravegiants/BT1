# [M] ggit is vulnerable to Command Injection via the fetchTags(branch) API

## Summary
Severity: Medium
Advisory: GHSA-62cx-5xj4-wfm4
CVE: CVE-2024-21532
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-10-08
Source: https://github.com/advisories/GHSA-62cx-5xj4-wfm4
Type: github-advisory

## Affected
- npm: `ggit` — affected >=0

## Details
All versions of the package ggit are vulnerable to Command Injection via the fetchTags(branch) API, which allows user input to specify the branch to be fetched and then concatenates this string along with a git command which is then passed to the unsafe exec() Node.js child process API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21532
- https://gist.github.com/lirantal/d8f87b366d2078e6118ab7bf2b005f02
- https://github.com/bahmutov/ggit
- https://security.snyk.io/vuln/SNYK-JS-GGIT-5731320
