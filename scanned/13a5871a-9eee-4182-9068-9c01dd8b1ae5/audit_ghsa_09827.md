# [H] LiteLLM: Authenticated command execution via MCP stdio test endpoints

## Summary
Severity: High
Advisory: GHSA-v4p8-mg3p-g94g
CVE: CVE-2026-42271
CWE: CWE-77, CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-v4p8-mg3p-g94g
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=1.74.2 <1.83.7

## Details
### Impact

Two endpoints used to preview an MCP server before saving it — `POST /mcp-rest/test/connection` and `POST /mcp-rest/test/tools/list` — accepted a full server configuration in the request body, including the `command`, `args`, and `env` fields used by the stdio transport. When called with a stdio configuration, the endpoints attempted to connect, which spawned the supplied command as a subprocess on the proxy host with the privileges of the proxy process.

The endpoints were gated only by a valid proxy API key, with no role check. Any authenticated user — including holders of low-privilege internal-user keys — could therefore run arbitrary commands on the host.

### Patches

Fixed in **`1.83.7`**. Both test endpoints now require the `PROXY_ADMIN` role, bringing them into line with the save endpoint.

### Workarounds

If upgrading is not immediately possible, developers should block `POST /mcp-rest/test/connection` and `POST /mcp-rest/test/tools/list` at their reverse proxy or API gateway.

## References
- https://github.com/BerriAI/litellm/security/advisories/GHSA-v4p8-mg3p-g94g
- https://nvd.nist.gov/vuln/detail/CVE-2026-42271
- https://github.com/BerriAI/litellm
- https://github.com/BerriAI/litellm/releases/tag/v1.83.7-stable
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2026-42271
