# [H] create-choo-app3 is vulnerable to Command Injection via the devInstall function

## Summary
Severity: High
Advisory: GHSA-rj7m-2p3g-fjxg
CVE: CVE-2022-25855
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-06
Source: https://github.com/advisories/GHSA-rj7m-2p3g-fjxg
Type: github-advisory

## Affected
- npm: `create-choo-app3` — affected >=0

## Details
All versions of the package create-choo-app3 are vulnerable to Command Injection via the devInstall function due to improper user-input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25855
- https://github.com/choojs/create-choo-app
- https://security.snyk.io/vuln/SNYK-JS-CREATECHOOAPP3-3157951
