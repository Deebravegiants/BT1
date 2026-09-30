# [M] n8n: Wrong OAuth Scope On Evaluations Test Run Creation Endpoint

## Summary
Severity: Medium
Advisory: GHSA-hv7x-3x78-gx53
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-hv7x-3x78-gx53
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.55
- npm: `n8n` — affected >=2.26.0 <2.26.2
- npm: `n8n` — affected >=2.0.0-rc.0 <2.25.7

## Details
## Impact
The `POST /workflows/{workflowId}/test-runs/new` endpoint authorized access using `workflow:read` rather than `workflow:execute`. An authenticated user with read-only access to a workflow could trigger a real evaluation test run, causing the workflow to execute via the internal workflow runner. This could result in unintended outbound API calls, data mutations, or other side effects in downstream systems connected to the workflow.

This issue primarily affects instances where the Evaluations feature is in use and where users may have `workflow:read` access without `workflow:execute` access, such as deployments using RBAC project roles.

## Patches
The issue has been fixed in n8n versions 1.123.55, 2.25.7, and 2.26.2. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict workflow access to fully trusted users only.
- Audit project role assignments and limit `workflow:read` access on sensitive workflows to users who should also be permitted to execute them.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-hv7x-3x78-gx53
- https://github.com/n8n-io/n8n
