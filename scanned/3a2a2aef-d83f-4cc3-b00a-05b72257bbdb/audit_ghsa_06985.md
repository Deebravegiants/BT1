# [H] n8n: Expression sandbox escape via arrow-function bodies enabling command execution

## Summary
Severity: High
Advisory: GHSA-gv7g-jm28-cr3m
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-gv7g-jm28-cr3m
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.32.0 <2.32.1
- npm: `n8n` — affected >=0 <2.31.5

## Details
## Impact

An authenticated user with permission to create or modify workflows could abuse crafted expressions using arrow functions to bypass the expression sandbox, triggering unintended system command execution on the host running n8n.

## Patches

The issue has been fixed in n8n versions 2.31.5 and 2.32.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds

If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict n8n instance access to fully trusted users only.
- Restrict workflow creation and editing permissions to fully trusted users only.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-gv7g-jm28-cr3m
- https://github.com/n8n-io/n8n/commit/f69dfc6dd2178a14ea1624d2e1d403c2e755042f
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.31.5
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.32.1
