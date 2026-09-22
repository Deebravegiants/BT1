# [M] n8n: Cross-Tenant Module-Cache Poisoning in the JS Task Runner

## Summary
Severity: Medium
Advisory: GHSA-9cmh-xcqm-5hqr
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-9cmh-xcqm-5hqr
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.67
- npm: `n8n` — affected >=2.32.0 <2.32.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.31.5

## Details
## Impact

n8n's JavaScript task runner shared one module cache across all users' Code-node executions, so a user able to run a Code node could poison a cached module and alter other users' Code-node executions on the same runner, affecting their confidentiality, integrity, or availability.

This is a cross-user isolation break within a single n8n instance. It does not constitute a sandbox escape or remote code execution. All multi-user n8n instances running the JS task runner with built-in or external modules enabled are affected.

## Patches

The issue has been fixed in n8n versions 1.123.67, 2.31.5, and 2.32.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds

If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict n8n instance access to fully trusted users only.
- Disable built-in and external module access in Code nodes by unsetting `NODE_FUNCTION_ALLOW_BUILTIN` and `NODE_FUNCTION_ALLOW_EXTERNAL`, which removes the poisonable module surface.
- Use the external runner mode with a dedicated runner per user or project if your deployment supports it.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-9cmh-xcqm-5hqr
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.67
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.31.5
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.32.1
