# [M] n8n: Wrong OAuth Scope on Evaluation Test Runs Endpoints

## Summary
Severity: Medium
Advisory: GHSA-664h-gpgq-h6xx
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-664h-gpgq-h6xx
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.55
- npm: `n8n` — affected >=2.26.0 <2.26.2
- npm: `n8n` — affected >=2.0.0-rc.0 <2.25.7

## Details
## Impact
Three mutating endpoints in the evaluation test runs controller authorized state-changing actions using `workflow:read` instead of the action-appropriate `workflow:execute` scope. An authenticated user with `project:viewer` role on a project could start new evaluation test runs, cancel in-flight runs, and delete run records for workflows they only had read access to.

This issue only affects instances with Advanced Permissions (Enterprise/Cloud) where projects and viewer roles are in use.

## Patches
The issue has been fixed in n8n versions 1.123.55, 2.25.7, and 2.26.2. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict project membership to fully trusted users only.
- Avoid granting viewer access to projects containing sensitive workflows.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-664h-gpgq-h6xx
- https://github.com/n8n-io/n8n
