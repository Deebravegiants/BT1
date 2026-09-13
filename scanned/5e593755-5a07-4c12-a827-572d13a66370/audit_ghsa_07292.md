# [H] n8n: Privilege Escalation and Code Execution via Full Public API Key Scope Assignment to Token Exchange JWTs

## Summary
Severity: High
Advisory: GHSA-777w-rpr6-c52h
CVE: CVE-2026-65595
CWE: CWE-269
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:L/SA:L (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-777w-rpr6-c52h
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.30.0 <2.30.1
- npm: `n8n` — affected >=0 <2.29.8

## Details
## Impact

JWTs issued through the Token Exchange module were assigned all Public API key scopes, regardless of the acting user's actual role. A low-privileged user who could obtain a valid external JWT trusted by a configured issuer could therefore use the resulting access token to invoke administrator-only Public API operations, such as role escalation, user creation, and user deletion.

The issue only affects instances where the Token Exchange feature and the Public API are enabled (N8N_TOKEN_EXCHANGE_ENABLED=true, N8N_ENV_FEAT_TOKEN_EXCHANGE=true) and the attacker can obtain an external JWT accepted by a configured trusted key. Role escalation additionally requires an Advanced Permissions license; Community Package installation additionally requires `N8N_COMMUNITY_PACKAGES_ENABLED=true` and `N8N_UNVERIFIED_PACKAGES_ENABLED=true`.

## Patches

The issue has been fixed in n8n version 2.30.1 and 2.29.8. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds

If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Disable the Token Exchange feature by setting `N8N_TOKEN_EXCHANGE_ENABLED=false` or `N8N_ENV_FEAT_TOKEN_EXCHANGE=false`.
- If Token Exchange cannot be disabled, restrict Public API access at the network level to trusted clients only.
- Disable unverified Community Package installation by setting `N8N_UNVERIFIED_PACKAGES_ENABLED=false` to eliminate the code execution path.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-777w-rpr6-c52h
- https://nvd.nist.gov/vuln/detail/CVE-2026-65595
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.29.8
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.30.1
- https://www.vulncheck.com/advisories/n8n-before-privilege-escalation-via-token-exchange
