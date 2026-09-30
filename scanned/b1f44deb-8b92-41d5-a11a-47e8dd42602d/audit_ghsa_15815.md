# [M] ggit is vulnerable to Arbitrary Argument Injection via the clone() API 

## Summary
Severity: Medium
Advisory: GHSA-pr45-cg4x-ff4m
CVE: CVE-2024-21533
CWE: CWE-88
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-10-08
Source: https://github.com/advisories/GHSA-pr45-cg4x-ff4m
Type: github-advisory

## Affected
- npm: `ggit` — affected >=0

## Details
All versions of the package ggit are vulnerable to Arbitrary Argument Injection via the clone() API, which allows specifying the remote URL to clone and the file on disk to clone to. The library does not sanitize for user input or validate a given URL scheme, nor does it properly pass command-line flags to the git binary using the double-dash POSIX characters (--) to communicate the end of options.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21533
- https://gist.github.com/lirantal/80c6d59ac1b682a32bc9d2ff92044bb9
- https://github.com/bahmutov/ggit
- https://security.snyk.io/vuln/SNYK-JS-GGIT-5731319
