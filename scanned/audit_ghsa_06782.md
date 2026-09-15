# [H] LiteLLM: MCP Authentication Bypass via OAuth2 Passthrough Fallback

## Summary
Severity: High
Advisory: GHSA-7488-6r32-c95q
CVE: CVE-2026-59822
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-7488-6r32-c95q
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=0 <1.84.0

## Details
### Impact

LiteLLM's MCP Streamable HTTP endpoint could allow an unauthenticated attacker to establish an authenticated MCP session using an arbitrary Bearer token.

The MCP auth handler supported OAuth2 passthrough for upstream MCP servers, but the fallback path could replace failed LiteLLM key validation with an empty `UserAPIKeyAuth()` object. This allowed requests with a fabricated `Authorization` header to reach MCP tooling without a valid LiteLLM key.

An attacker could use this to list and call configured MCP tools and access connected services exposed through MCP.

### Patches

The issue is fixed in `1.84.0`.

We recommend upgrading to `1.84.0` or later.

### Workarounds

If upgrading is not immediately possible, disable MCP routes or block access to `/mcp/` and related MCP endpoints at your reverse proxy or API gateway.

### References

* [v1.84.0](https://github.com/BerriAI/litellm/releases/tag/v1.84.0)

## References
- https://github.com/BerriAI/litellm/security/advisories/GHSA-7488-6r32-c95q
- https://nvd.nist.gov/vuln/detail/CVE-2026-59822
- https://github.com/BerriAI/litellm/pull/26463
- https://github.com/BerriAI/litellm/commit/73869f0faf7d11ee21adcb5f91b8c33a340b6c2c
- https://github.com/BerriAI/litellm
- https://github.com/BerriAI/litellm/releases/tag/v1.84.0
