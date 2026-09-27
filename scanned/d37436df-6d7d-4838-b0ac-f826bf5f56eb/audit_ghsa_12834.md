# [H] window-control vulnerable to Command Injection due to improper input sanitization

## Summary
Severity: High
Advisory: GHSA-9mjx-wfqp-j5ph
CVE: CVE-2022-25926
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-04
Source: https://github.com/advisories/GHSA-9mjx-wfqp-j5ph
Type: github-advisory

## Affected
- npm: `window-control` — affected >=0 <1.4.5

## Details
window-control is an npm package that provides tools to manage window focus. Versions before 1.4.5 are vulnerable to Command Injection via the `sendKeys` function due to improper input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25926
- https://github.com/bruno-robert/window-control/commit/075c854534a749d887655a906759f5a7eee95173
- https://github.com/bruno-robert/window-control
- https://github.com/bruno-robert/window-control/releases/tag/v1.4.5
- https://security.snyk.io/vuln/SNYK-JS-WINDOWCONTROL-3186345
