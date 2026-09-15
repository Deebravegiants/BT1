# [M] n8n has an SSO Enforcement Bypass in its Self-Service Settings API

## Summary
Severity: Medium
Advisory: GHSA-vjf3-2gpj-233v
CWE: CWE-269, CWE-284, CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-vjf3-2gpj-233v
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <2.8.0

## Details
## Impact
An authenticated user signed in through Single Sign-On (SSO) could disable SSO enforcement for their own account through the n8n API. This allowed the user to create a local password and authenticate directly with email and password, completely bypassing the organization's SSO policy, centralized identity management, and any identity-provider-enforced multi-factor authentication.

## Patches
The issue has been fixed in n8n version 2.8.0. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Monitor audit logs for users who create local credentials after authenticating via SSO.
- Restrict the n8n instance to fully trusted users only.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-vjf3-2gpj-233v
- https://github.com/n8n-io/n8n/commit/a70b2ea379086da3de103bb84811e88cadf29976
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.8.0
