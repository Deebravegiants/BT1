# [M] Cross-site Scripting in vmd

## Summary
Severity: Medium
Advisory: GHSA-pfr3-87q3-65rc
CVE: CVE-2021-33041
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-pfr3-87q3-65rc
Type: github-advisory

## Affected
- npm: `vmd` — affected >=0

## Details
vmd through 1.34.0 allows `div class="markdown-body"` XSS, as demonstrated by Electron remote code execution via `require('child_process').execSync('calc.exe')` on Windows and a similar attack on macOS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33041
- https://github.com/yoshuawuyts/vmd/issues/137
- https://www.npmjs.com/package/vmd
