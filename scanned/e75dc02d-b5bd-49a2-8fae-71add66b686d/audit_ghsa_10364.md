# [H] n8n-mcp's IPv4-mapped IPv6 addresses bypass SSRF protection in validateUrlSync(), enabling full SSRF for SDK embedders

## Summary
Severity: High
Advisory: GHSA-56c3-vfp2-5qqj
CVE: CVE-2026-42449
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-30
Source: https://github.com/advisories/GHSA-56c3-vfp2-5qqj
Type: github-advisory

## Affected
- npm: `n8n-mcp` — affected >=2.47.4 <2.47.14

## Details
### Impact

In the SDK embedder path (`N8NDocumentationMCPServer` constructor, `getN8nApiClient()`, and `validateInstanceContext()`), the synchronous URL validator in `SSRFProtection.validateUrlSync()` had no IPv6 checks. IPv4-mapped IPv6 addresses such as `http://[::ffff:169.254.169.254]` bypassed the cloud-metadata, localhost, and private-IP range checks. An attacker able to supply an `n8nApiUrl` value could cause the server to issue HTTP requests to cloud metadata endpoints (AWS IMDS, GCP, Azure, Alibaba, Oracle), RFC1918 private networks, or localhost services. Response bodies are returned to the caller (non-blind SSRF), and the `n8nApiKey` is forwarded in the `x-n8n-api-key` header to the attacker-controlled target.

The first-party HTTP server deployment was not primarily affected — it has a second async validator (`validateWebhookUrl`) that catches IPv6 addresses.

Impact category: **CWE-918** (Server-Side Request Forgery).

### Affected

Deployments embedding n8n-mcp as an SDK using `N8NDocumentationMCPServer` or `N8NMCPEngine` with user-supplied `InstanceContext` on versions **v2.47.4 through v2.47.13**.

### Patched

**v2.47.14** and later.

- npm: `npx n8n-mcp@latest` (or pin to `>= 2.47.14`)
- Docker: `docker pull ghcr.io/czlonkowski/n8n-mcp:latest`

### Workarounds

If developers cannot upgrade immediately:

- **Validate URLs before passing to the SDK** — reject any `n8nApiUrl` whose hostname is an IP literal (bracketed IPv6 or dotted IPv4) before calling `N8NDocumentationMCPServer` / `getN8nApiClient()`. Accept only URLs with DNS-resolvable hostnames.
- **Restrict egress at the network layer** — block outbound traffic from the n8n-mcp process to RFC1918 ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16), link-local `169.254.0.0/16`, and cloud metadata endpoints. Defense-in-depth against this class of issue and recommended even after upgrading.
- **Do not accept user-controlled `n8nApiUrl` values** — if the project's integration derives the URL from internal configuration only, this vulnerability is not reachable.

Upgrading to v2.47.14 is still strongly recommended.

### Credit

Reported by @manthanghasadiya.

## References
- https://github.com/czlonkowski/n8n-mcp/security/advisories/GHSA-56c3-vfp2-5qqj
- https://nvd.nist.gov/vuln/detail/CVE-2026-42449
- https://github.com/czlonkowski/n8n-mcp/commit/9639f757853149f0cb16663cc8b6b6468f27a25f
- https://github.com/czlonkowski/n8n-mcp
