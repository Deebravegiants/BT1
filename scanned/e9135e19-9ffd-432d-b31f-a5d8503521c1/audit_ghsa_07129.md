# [H] n8n: Bypass "Allowed HTTP Request Domains" Credential Restriction in Multiple AI and LLM Nodes

## Summary
Severity: High
Advisory: GHSA-64xh-79j6-r5v8
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-64xh-79j6-r5v8
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.32.0 <2.32.1
- npm: `n8n` — affected >=0 <2.31.5

## Details
## Impact

The credential "Allowed HTTP Request Domains" allowlist was intended to restrict which hosts a credential's secret could be sent to, protecting shared credentials from users who could use but not view them. Several AI/LLM nodes did not enforce this allowlist when a user-supplied base or endpoint URL was set. A low-privileged workflow editor with use-only access to such a shared credential could point one of these nodes at an attacker-controlled host and cause the credential secret to be transmitted there, then reuse it against the underlying service.

Only instances where a credential has "Allowed HTTP Request Domains" configured and is shared with non-owner users are affected.

## Patches
The issue has been fixed in n8n versions 2.31.5 and 2.32.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict workflow creation and editing permissions to fully trusted users only.
- Restrict credential sharing to fully trusted users only.
- Audit credentials with domain restrictions for unexpected sharing relationships.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-64xh-79j6-r5v8
- https://github.com/n8n-io/n8n/commit/f69dfc6dd2178a14ea1624d2e1d403c2e755042f
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.31.5
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.32.1
