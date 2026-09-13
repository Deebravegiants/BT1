# [H] n8n-mcp webhook and API client paths has an authenticated SSRF

## Summary
Severity: High
Advisory: GHSA-cmrh-wvq6-wm9r
CVE: CVE-2026-44694
CWE: CWE-367, CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:L/VA:L/SC:H/SI:L/SA:L (CVSS_V4)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-cmrh-wvq6-wm9r
Type: github-advisory

## Affected
- npm: `n8n-mcp` — affected >=2.18.7 <2.50.2

## Details
### Summary

Authenticated Server-Side Request Forgery affecting the webhook trigger tools, the n8n API client (`N8N_API_URL`), and per-request URLs supplied via the `x-n8n-url` header in multi-tenant HTTP mode.

### Impact

A caller with access to the MCP session can drive HTTP requests from the n8n-mcp host to internal services and cloud metadata endpoints that the SSRF gate is meant to block. The response body is returned to the caller, making internal-service enumeration and credential theft immediate without any out-of-band channel.

- **Multi-tenant HTTP deployments** where tenants share an `AUTH_TOKEN`: any tenant with valid credentials can reach the operator's cloud metadata service and exfiltrate temporary IAM / GCP service account / Azure managed-identity credentials.
- **Single-tenant deployments**: indirect prompt injection through tool arguments reaches the same surface; an attacker who can influence the LLM's tool calls can read internal services from the n8n-mcp host.
- **Stdio deployments** are reachable via the same prompt-injection path.

### Patched Versions

Fixed in `n8n-mcp@2.50.2`.

**Note for operators:** The same SSRF gate that previously covered webhook URLs now also covers the n8n API client base URL. If `N8N_API_URL` points at `http://localhost:5678` (n8n on the same host) or an RFC1918 address (n8n on the same private network), set `WEBHOOK_SECURITY_MODE=moderate` (allows localhost, still blocks RFC1918 and cloud metadata) or `WEBHOOK_SECURITY_MODE=permissive` (allows RFC1918 too — only safe on a trusted private network). Default `strict` is correct for deployments where n8n is reachable at a public hostname.

### Workarounds

For deployments that cannot upgrade immediately:

1. **Restrict network egress** from the n8n-mcp host with a firewall, reverse proxy, or cloud security group. Explicitly deny cloud metadata IPs (`169.254.169.254`, `169.254.170.2`, `100.100.100.200`, `192.0.0.192`, and the GCP `metadata.google.internal` resolved IP) and any RFC1918 networks the server does not legitimately need to reach.
2. **Run in stdio mode** instead of HTTP if the multi-tenant surface is not needed (no shared `AUTH_TOKEN` to compromise).
3. **Disable workflow management tools** via `DISABLED_TOOLS=n8n_trigger_webhook_workflow,n8n_create_workflow,n8n_test_workflow` if the deployment does not need them.

### Credit

Reported by [@fg0x0](https://github.com/fg0x0).

## References
- https://github.com/czlonkowski/n8n-mcp/security/advisories/GHSA-cmrh-wvq6-wm9r
- https://nvd.nist.gov/vuln/detail/CVE-2026-44694
- https://github.com/czlonkowski/n8n-mcp/commit/bcaba839409d470abeb4a6ad9b361b553a1098eb
- https://github.com/czlonkowski/n8n-mcp
- https://github.com/czlonkowski/n8n-mcp/releases/tag/v2.50.2
