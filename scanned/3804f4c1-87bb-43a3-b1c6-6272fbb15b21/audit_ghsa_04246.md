# [M] n8n: Python Code Node AST Validator Bypass

## Summary
Severity: Medium
Advisory: GHSA-jwm3-qcfw-c5pp
CWE: CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-jwm3-qcfw-c5pp
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.26.0 <2.26.2
- npm: `n8n` — affected >=0 <2.25.7

## Details
## Impact
An authenticated user with permission to create or modify workflows containing a Python Code node could bypass the AST security validator and access the task executor module namespace. On self-hosted instances where `N8N_BLOCK_RUNNER_ENV_ACCESS=false` is set, this extended to disclosure of environment variables accessible to the task runner process.

This issue only affects instances where the Python Task Runner is enabled and `N8N_BLOCK_RUNNER_ENV_ACCESS=true`.

## Patches
The issue has been fixed in n8n versions 2.25.7, and 2.26.2. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the Python Code node by adding `n8n-nodes-base.code` to the `NODES_EXCLUDE` environment variable, or disable the Python Task Runner entirely.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-jwm3-qcfw-c5pp
- https://github.com/n8n-io/n8n
