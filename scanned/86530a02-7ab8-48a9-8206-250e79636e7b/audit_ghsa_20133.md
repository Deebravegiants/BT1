# [H] abacus-ext-cmdline vulnerable to Command Injection

## Summary
Severity: High
Advisory: GHSA-m5v8-wpw4-rj3x
CVE: CVE-2022-24431
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-21
Source: https://github.com/advisories/GHSA-m5v8-wpw4-rj3x
Type: github-advisory

## Affected
- npm: `abacus-ext-cmdline` — affected >=0

## Details
All versions of package abacus-ext-cmdline are vulnerable to Command Injection via the execute function due to improper user-input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24431
- https://security.snyk.io/vuln/SNYK-JS-ABACUSEXTCMDLINE-3157950
