# [C] Command Injection in create-choo-electron

## Summary
Severity: Critical
Advisory: GHSA-j8wr-fwf2-vvr9
CVE: CVE-2022-25908
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-j8wr-fwf2-vvr9
Type: github-advisory

## Affected
- npm: `create-choo-electron` — affected >=0

## Details
All versions of the package create-choo-electron are vulnerable to Command Injection via the devInstall function due to improper user-input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25908
- https://security.snyk.io/vuln/SNYK-JS-CREATECHOOELECTRON-3157953
