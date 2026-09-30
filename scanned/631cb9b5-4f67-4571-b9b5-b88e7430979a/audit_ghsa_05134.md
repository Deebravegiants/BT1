# [H] n8n: Cross-Tenant Credential Takeover via Dynamic Credentials EE Endpoints

## Summary
Severity: High
Advisory: GHSA-2j5h-858j-5mpf
CVE: CVE-2026-54305
CWE: CWE-200, CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-2j5h-858j-5mpf
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.55
- npm: `n8n` — affected >=2.26.0 <2.26.2
- npm: `n8n` — affected >=2.0.0-rc.0 <2.25.7

## Details
## Impact
Three EE endpoints used by the Dynamic Credentials feature accepted any authenticated n8n session without performing per-resource ownership or scope checks on the target workflow or credential. An authenticated user with no project membership or credential sharing relationship could enumerate credential identifiers, names, and types referenced by any private workflow in the instance, initiate an OAuth authorization flow against another user's credential to overwrite its stored tokens with tokens bound to an account they control, or revoke another user's stored credential tokens entirely.

Workflows relying on a hijacked credential would subsequently execute under the attacker's OAuth identity, enabling data exfiltration to attacker-controlled external services and persistent takeover of integrations. Token revocation would break affected workflows.

This issue only affects Enterprise instances where the Dynamic Credentials feature is enabled.

## Patches
The issue has been fixed in n8n versions 1.123.55, 2.25.7, and 2.26.2. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict n8n instance access to fully trusted users only.
- If the Dynamic Credentials feature is not actively required, disable it by unsetting `N8N_ENV_FEAT_DYNAMIC_CREDENTIALS`.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

---
n8n has adopted CVSS 4.0 as primary score for all security advisories. CVSS 3.1 vector strings are provided for backwards compatibility.

CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-2j5h-858j-5mpf
- https://nvd.nist.gov/vuln/detail/CVE-2026-54305
- https://github.com/n8n-io/n8n
