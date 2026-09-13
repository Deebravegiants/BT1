# [M] SearXNG MCP Server is Vulnerable to SSRF in web_url_read: the internal-address guard is disabled by default (MCP_HTTP_HARDEN off)

## Summary
Severity: Medium
Advisory: GHSA-q87f-qc2r-2gw4
CVE: CVE-2026-54688
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-19
Source: https://github.com/advisories/GHSA-q87f-qc2r-2gw4
Type: github-advisory

## Affected
- npm: `mcp-searxng` — affected >=0 <1.2.1

## Details
Ref: https://github.com/ihor-sokoliuk/mcp-searxng/issues/87#issuecomment-4645453694


### Summary
The web_url_read tool fetches a caller-supplied URL server-side and converts it to markdown. An SSRF guard (assertUrlAllowed, which blocks private/loopback/metadata addresses) exists but runs only when MCP_HTTP_HARDEN=true, which is off by default. So in the default configuration there is no internal-address filtering, and an attacker who can influence the URL can make the server fetch internal services and cloud metadata and return their content. Confirmed on 1.1.0 (default config): web_url_read fetched a local internal sentinel and returned its content.

### Details
dist/index.js (around lines 90-101): web_url_read calls fetchAndConvertToMarkdown on the caller URL. dist/url-reader.js (around lines 44-52): assertUrlAllowed performs the private-IP/loopback check, but only when the hardening flag is set; dist/http-security.js (around line 11) defaults MCP_HTTP_HARDEN to off. With the default config the check is skipped entirely. Even when enabled, the check is literal-hostname based with no DNS-rebinding or redirect re-check (the fetch follows redirects). file:// is rejected, so this is HTTP/HTTPS SSRF.

### PoC
Re-validated on mcp-searxng 1.1.0 over MCP stdio in the default configuration (MCP_HTTP_HARDEN not set):
```
tools: searxng_web_search, web_url_read
web_url_read({ url: "http://127.0.0.1:<port>/internal" }) -> server fetched the internal sentinel; SSRF: CONFIRMED
```
The server fetched the loopback sentinel and returned its content. With MCP_HTTP_HARDEN=true the same request is blocked (policy error), confirming the guard exists but ships off. The same reaches http://169.254.169.254/... on cloud hosts.

### Impact
In the default configuration an attacker who can influence the URL (LLM-produced and steerable via prompt injection) can make the server fetch internal-only HTTP services and the cloud metadata endpoint, returning their contents into the model context for exfiltration. The protection that would prevent it is not enabled by default.

### Remediation
Enable the internal-address filtering by default (fail safe): make assertUrlAllowed run unconditionally and require an explicit opt-out only for trusted environments. Strengthen the check to resolve the host and reject loopback, link-local/metadata (169.254.0.0/16), 0.0.0.0/8, and private ranges, and re-validate on every redirect hop (or pin to the validated IP).

## References
- https://github.com/ihor-sokoliuk/mcp-searxng/security/advisories/GHSA-q87f-qc2r-2gw4
- https://github.com/ihor-sokoliuk/mcp-searxng/issues/87#issuecomment-4645453694
- https://github.com/ihor-sokoliuk/mcp-searxng
- https://github.com/ihor-sokoliuk/mcp-searxng/releases/tag/v1.2.1
