# [H] n8n: Account Takeover via Unverified Email Claim in Token Exchange Embed Login

## Summary
Severity: High
Advisory: GHSA-8342-988q-86cr
CWE: CWE-345, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:L (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-8342-988q-86cr
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.32.0 <2.32.1
- npm: `n8n` — affected >=0 <2.31.5

## Details
## Impact

In an n8n instance, when a validly-signed incoming token was matched to a local account by its email claim, the service did not check that the trusted key's permitted role ceiling covered that account, nor that the email claim was verified. As a result, anyone able to obtain a token accepted by one of the configured trusted keys, for example a trusted issuer that emitted unverified email addresses, could authenticate as any existing user, gaining full account control.

This issue only affects instances where the embed login feature is enabled and at least one trusted key source is configured.

## Patches

The issue has been fixed in n8n version 2.32.1. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds

If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Disable the embed login feature by setting `N8N_TOKEN_EXCHANGE_ENABLED=false`.
- If embed login cannot be disabled, restrict network access to the n8n instance to fully trusted parties only, and audit all configured trusted keys and their `allowedRoles` assignments.
- Review `auth_identity` records for unexpected `token-exchange` entries linked to high-privilege accounts.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-8342-988q-86cr
- https://github.com/n8n-io/n8n/commit/f69dfc6dd2178a14ea1624d2e1d403c2e755042f
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.31.5
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.32.1
