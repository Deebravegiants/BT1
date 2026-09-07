# [M] Toast UI Grid vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-9rwj-9j2h-fhvm
CVE: CVE-2022-23458
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-23
Source: https://github.com/advisories/GHSA-9rwj-9j2h-fhvm
Type: github-advisory

## Affected
- npm: `tui-grid` — affected >=0 <4.21.3

## Details
Toast UI Grid is a component to display and edit data. Versions prior to 4.21.3 are vulnerable to cross-site scripting attacks when pasting specially crafted content into editable cells. This issue was fixed in version 4.21.3. There are no known workarounds.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23458
- https://github.com/nhn/tui.grid/commit/e9db5968675ae113c07efc091cce210f2b26854f
- https://github.com/nhn/tui.grid
- https://securitylab.github.com/advisories/GHSL-2022-029_nhn_tui_grid
