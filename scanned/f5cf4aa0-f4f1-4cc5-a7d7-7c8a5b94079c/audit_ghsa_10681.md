# [M] n8n has Public API Variables IDOR that Allows Cross-Project Secret Disclosure

## Summary
Severity: Medium
Advisory: GHSA-756q-gq9h-fp22
CVE: CVE-2026-42227
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-756q-gq9h-fp22
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.32
- npm: `n8n` — affected >=2.18.0 <2.18.1
- npm: `n8n` — affected >=2.0.0 <2.17.4

## Details
## Impact
An authenticated user with a valid API key scoped to `variable:list` could read variables from projects they are not a member of by supplying an arbitrary `projectId` query parameter to the public API variables endpoint. The handler queried the variables repository directly without enforcing project membership checks, bypassing the authorization-aware service layer used by the internal enterprise controller. 

If variables were misused to store sensitive information such as credentials or tokens, they should be rotated immediately.

This issue only affects licensed enterprise or team deployments with multiple projects and the variables feature enabled.

## Patches
The issue has been fixed in n8n versions 1.123.32, 2.17.4, and 2.18.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:

- Restrict n8n access and API key issuance to fully trusted users only.
- Audit existing project variables for sensitive values and rotate any secrets that may have been exposed.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-756q-gq9h-fp22
- https://nvd.nist.gov/vuln/detail/CVE-2026-42227
- https://github.com/n8n-io/n8n
