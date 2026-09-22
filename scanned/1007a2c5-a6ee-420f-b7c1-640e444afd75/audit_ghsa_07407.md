# [H] n8n: Cross-Issuer Token Exchange Account Binding via Subject-Only Identity Resolution

## Summary
Severity: High
Advisory: GHSA-mq3m-f8x3-579w
CVE: CVE-2026-59208
CWE: CWE-287, CWE-346
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-mq3m-f8x3-579w
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.28.0 <2.28.1
- npm: `n8n` — affected >=0 <2.27.4

## Details
## Impact
When an n8n instance is configured with more than one trusted token-exchange issuer, external identities are resolved to local accounts using only the JWT `sub` claim, ignoring the issuer (`iss`). As a result, two different issuers that emit the same subject value map to the same local account.

An attacker who can obtain a valid token from one trusted issuer with a `sub` matching a victim registered under a different issuer can authenticate as that victim and access their account.

This issue only affects instances where the token exchange feature is enabled and more than one trusted external issuer is configured.

## Patches
The issue has been fixed in n8n version 2.28.1. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- If multiple trusted issuers are not required, reduce the token exchange configuration to a single trusted issuer.
- Disable the token exchange feature entirely if it is not in active use.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-mq3m-f8x3-579w
- https://nvd.nist.gov/vuln/detail/CVE-2026-59208
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.27.4
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.28.1
