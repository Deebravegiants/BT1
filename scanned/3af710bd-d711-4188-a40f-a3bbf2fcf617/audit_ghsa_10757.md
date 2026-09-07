# [H] LiteLLM: Server-Side Template Injection in /prompts/test endpoint

## Summary
Severity: High
Advisory: GHSA-xqmj-j6mv-4862
CVE: CVE-2026-42203
CWE: CWE-1336
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-xqmj-j6mv-4862
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=1.80.5 <1.83.7

## Details
### Impact
The `POST /prompts/test` endpoint accepted user-supplied prompt templates and rendered them without sandboxing. A crafted template could run arbitrary code inside the LiteLLM Proxy process.

The endpoint only checks that the caller presents a valid proxy API key, so any authenticated user could reach it. Depending on how the proxy is deployed, this could expose secrets in the process environment (such as provider API keys or database credentials) and allow commands to be run on the host.

Proxy deployments running an affected version are in scope.

### Patches
The issue is fixed in **`1.83.7-stable`**. The fix switches the prompt template renderer to a sandboxed environment that blocks the attributes this attack relies on.

LiteLLM recommends upgrading to `1.83.7-stable` or later.

### Workarounds
If upgrading is not immediately possible:

1. Block `POST /prompts/test` at your reverse proxy or API gateway.
2. Review and rotate API keys that should not have access to prompt management routes.

## References
- https://github.com/BerriAI/litellm/security/advisories/GHSA-xqmj-j6mv-4862
- https://nvd.nist.gov/vuln/detail/CVE-2026-42203
- https://github.com/BerriAI/litellm
- https://github.com/BerriAI/litellm/releases/tag/v1.83.7-stable
