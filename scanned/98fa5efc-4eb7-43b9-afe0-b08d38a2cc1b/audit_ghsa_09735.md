# [H] n8n Vulnerable to Unauthenticated Denial of Service via MCP Client Registration

## Summary
Severity: High
Advisory: GHSA-49m9-pgww-9vq6
CVE: CVE-2026-42236
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-49m9-pgww-9vq6
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.32
- npm: `n8n` — affected >=2.18.0 <2.18.1
- npm: `n8n` — affected >=2.0.0 <2.17.4

## Details
## Impact
The MCP OAuth client registration endpoint accepted unauthenticated requests and stored client data without adequate resource controls. An unauthenticated remote attacker could exhaust server memory resources by sending large registration payloads, rendering the n8n instance unavailable. The MCP enable/disable toggle gates MCP access but did not restrict client registrations, meaning the endpoint is reachable regardless of whether MCP access is enabled on the instance.

The patches address the unbound registration with an upper bound of registered clients and disabling creation when MCP is disabled on the instance. Mean to restrict the payload size of requests already exist and can be used to control additional risks.

## Patches
The issue has been fixed in n8n versions 1.123.32, 2.17.4, and 2.18.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict network access to the n8n instance to prevent requests from untrusted sources.
- Reduce the maximum accepted payload size by lowering the `N8N_PAYLOAD_SIZE_MAX` environment variable from its default value.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-49m9-pgww-9vq6
- https://nvd.nist.gov/vuln/detail/CVE-2026-42236
- https://github.com/n8n-io/n8n
