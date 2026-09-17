# [M] n8n: Merge Node SQL Mode Prototype Pollution

## Summary
Severity: Medium
Advisory: GHSA-9c38-2mcm-q7f7
CVE: CVE-2026-54311
CWE: CWE-488
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-9c38-2mcm-q7f7
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.26.0 <2.26.2
- npm: `n8n` — affected >=0 <2.25.7

## Details
## Impact
An authenticated user with permission to create or modify workflows could pollute the sandbox used by the Merge node's SQL Query mode. Because the sandbox context was cached and reused across all workflow executions on the instance, prototype mutations introduced by one user's workflow persist into subsequent Merge SQL executions belonging to other users or projects. This allowed a low-privileged attacker to intercept workflow data processed by other users on the same instance.

This issue only affects multi-user n8n instances where more than one user has permission to create and execute workflows containing the Merge node in SQL Query mode.

## Patches
The issue has been fixed in n8n versions 2.25.7, and 2.26.2. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the Merge node by adding `n8n-nodes-base.merge` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-9c38-2mcm-q7f7
- https://nvd.nist.gov/vuln/detail/CVE-2026-54311
- https://github.com/n8n-io/n8n
