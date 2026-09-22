# [H] n8n Has a Cross-user Authorization Bypass in Dynamic Credential OAuth Endpoints

## Summary
Severity: High
Advisory: GHSA-6h4j-wcr9-2vg7
CVE: CVE-2026-45732
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-6h4j-wcr9-2vg7
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.43
- npm: `n8n` — affected >=2.21.0 <2.21.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.20.7

## Details
## Impact
The OAuth1 and OAuth2 credential reconnect endpoints authorized access using `credential:read` rather than `credential:update`. An authenticated user with read-only access to a shared credential could initiate an OAuth reconnect flow and overwrite the stored token material for that credential with tokens bound to an external account they control. Workflows relying on the affected credential would subsequently execute under the attacker's OAuth identity, enabling data exfiltration to attacker-controlled external services and persistent takeover of shared integrations.

This issue affects instances where credentials are shared with other users or across projects.

## Patches
The issue has been fixed in n8n versions 1.123.43, 2.20.7, and 2.21.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict credential sharing to fully trusted users only.
- Audit shared credentials for unexpected OAuth token changes and revoke any tokens that may have been replaced.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

---
n8n has adopted CVSS 4.0 as primary score for all security advisories. CVSS 3.1 vector strings are provided for backwards compatibility.

CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-6h4j-wcr9-2vg7
- https://nvd.nist.gov/vuln/detail/CVE-2026-45732
- https://github.com/n8n-io/n8n
