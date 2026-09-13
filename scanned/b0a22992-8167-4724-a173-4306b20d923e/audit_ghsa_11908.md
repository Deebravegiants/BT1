# [M] n8n Has Authorization Bypass in OAuth Callback via N8N_SKIP_AUTH_ON_OAUTH_CALLBACK

## Summary
Severity: Medium
Advisory: GHSA-vpgc-2f6g-7w7x
CVE: CVE-2026-33720
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-vpgc-2f6g-7w7x
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <2.8.0

## Details
## Impact
When the `N8N_SKIP_AUTH_ON_OAUTH_CALLBACK` environment variable is set to `true`, the OAuth callback handler skips ownership verification of the OAuth state parameter. This allows an attacker to trick a victim into completing an OAuth flow against a credential object the attacker controls, causing the victim's OAuth tokens to be stored in the attacker's credential. The attacker can then use those tokens to execute workflows in their name.

- This issue only affects instances where `N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=true` is explicitly configured (non-default).

## Patches
The issue has been fixed in n8n version 2.8.0. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Avoid enabling `N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=true` unless strictly required.
- Restrict access to the n8n instance to fully trusted users only.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-vpgc-2f6g-7w7x
- https://nvd.nist.gov/vuln/detail/CVE-2026-33720
- https://github.com/n8n-io/n8n
