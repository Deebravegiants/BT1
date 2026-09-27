# [M] n8n: Public API Execution Retry Authorization Bypass

## Summary
Severity: Medium
Advisory: GHSA-h3jj-5f3v-3685
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-h3jj-5f3v-3685
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.26.0 <2.26.2
- npm: `n8n` — affected >=0 <2.25.7

## Details
## Impact
The Public API endpoint for retrying executions authorized access using `workflow:read` rather than `workflow:execute`. An authenticated user with read-only access to a shared workflow could use the Public API to retry executions of that workflow, bypassing the intended permission boundary between read and execute access.

This issue affects instances where workflows are shared with other users or across projects.

## Patches
The issue has been fixed in n8n versions 2.25.7, and 2.26.2. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict workflow sharing to fully trusted users only.
- Restrict network access to the n8n Public API to trusted users only.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-h3jj-5f3v-3685
- https://github.com/n8n-io/n8n
