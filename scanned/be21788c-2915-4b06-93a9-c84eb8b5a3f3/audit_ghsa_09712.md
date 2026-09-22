# [H] stata-mcp has insufficient validation of user-supplied Stata do-file content that can lead to command execution

## Summary
Severity: High
Advisory: GHSA-jpcj-7wfg-mqxv
CVE: CVE-2026-31040
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-jpcj-7wfg-mqxv
Type: github-advisory

## Affected
- PyPI: `stata-mcp` — affected >=0 <1.13.0

## Details
A vulnerability was identified in stata-mcp prior to v1.13.0 where insufficient validation of user-supplied Stata do-file content can lead to command execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31040
- https://github.com/SepineTam/stata-mcp/issues/20
- https://github.com/SepineTam/stata-mcp/pull/21
- https://github.com/SepineTam/stata-mcp/commit/52413ce
- https://github.com/SepineTam/stata-mcp/releases/tag/v1.13.0
- https://github.com/sepinetam/stata-mcp
