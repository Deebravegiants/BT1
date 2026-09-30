# [M] mcp-server-semgrep has a Command Injection issue

## Summary
Severity: Medium
Advisory: GHSA-86hp-qxqp-w9wv
CVE: CVE-2026-7446
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-30
Source: https://github.com/advisories/GHSA-86hp-qxqp-w9wv
Type: github-advisory

## Affected
- npm: `mcp-server-semgrep` — affected >=0 <1.0.1

## Details
A vulnerability was detected in VetCoders mcp-server-semgrep 1.0.0. This affects the function analyze_results/filter_results/export_results/compare_results/scan_directory/create_rule of the file src/index.ts of the component MCP Interface. The manipulation of the argument ID results in os command injection. The attack can be executed remotely. The exploit is now public and may be used. Upgrading to version 1.0.1 is able to mitigate this issue. The patch is identified as 141335da044e53c3f5b315e0386e01238405b771. It is advisable to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7446
- https://github.com/VetCoders/mcp-server-semgrep/issues/12
- https://github.com/VetCoders/mcp-server-semgrep/pull/15
- https://github.com/VetCoders/mcp-server-semgrep/commit/141335da044e53c3f5b315e0386e01238405b771
- https://github.com/VetCoders/mcp-server-semgrep
- https://github.com/VetCoders/mcp-server-semgrep/releases/tag/v1.0.1
- https://vuldb.com/submit/804100
- https://vuldb.com/vuln/360187
- https://vuldb.com/vuln/360187/cti
