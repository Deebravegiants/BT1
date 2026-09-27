# [M] H3 has an Open Redirect via Protocol-Relative Path in redirectBack() Referer Validation

## Summary
Severity: Medium
Advisory: GHSA-fp4x-ggrf-wmc6
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-fp4x-ggrf-wmc6
Type: github-advisory

## Affected
- npm: `h3` — affected >=2.0.1-rc.17 <2.0.1-rc.18

## Details
## Summary

The `redirectBack()` utility in h3 validates that the `Referer` header shares the same origin as the request before using its pathname as the redirect `Location`. However, the pathname is not sanitized for protocol-relative paths (starting with `//`). An attacker can craft a same-origin URL with a double-slash path segment that passes the origin check but produces a `Location` header interpreted by browsers as a protocol-relative redirect to an external domain.

## Details

The vulnerable code is in `src/utils/response.ts:89-97`:

```typescript
export function redirectBack(
  event: H3Event,
  opts: { fallback?: string; status?: number; allowQuery?: boolean } = {},
): HTTPResponse {
  const referer = event.req.headers.get("referer");
  let location = opts.fallback ?? "/";
  if (referer && URL.canParse(referer)) {
    const refererURL = new URL(referer);
    if (refererURL.origin === event.url.origin) {
      // BUG: pathname can be "//evil.com/path" which browsers interpret
      // as a protocol-relative URL
      location = refererURL.pathname + (opts.allowQuery ? refererURL.search : "");
    }
  }
  return redirect(location, opts.status);
}
```

The root cause is a discrepancy between how the WHATWG URL parser and browsers handle double-slash paths:

1. `new URL("http://target.com//evil.com/path").origin` → `"http://target.com"` — origin check **passes**
2. `new URL("http://target.com//evil.com/path").pathname` → `"//evil.com/path"` — extracted as redirect location
3. Browser receives `Location: //evil.com/path` → interprets as protocol-relative URL → **redirects to `evil.com`**

**Attack scenario:** The attacker shares a link like `http://target.com//evil.com/page`. If the target application has catch-all routes (common in SPAs built with h3/Nitro), the app serves its page at that URL. When the user navigates to an endpoint calling `redirectBack()`, the browser sends `Referer: http://target.com//evil.com/page`. The origin check passes, and the user is redirected to `evil.com`, which can host a phishing page mimicking the target.

## PoC

```bash
# 1. Create a minimal h3 app with redirectBack
cat > /tmp/h3-redirect-poc.ts << 'SCRIPT'
import { H3, redirectBack } from "h3";

const app = new H3();
app.post("/submit", (event) => redirectBack(event));

const res = await app.fetch(new Request("http://localhost/submit", {
  method: "POST",
  headers: { referer: "http://localhost//evil.com/steal" }
}));

console.log("Status:", res.status);
console.log("Location:", res.headers.get("location"));
// Expected: a same-origin path
// Actual: "//evil.com/steal" — protocol-relative redirect to evil.com
SCRIPT

# 2. Verify URL parsing behavior
node -e "
const u = new URL('http://localhost//evil.com/steal');
console.log('origin:', u.origin);         // http://localhost
console.log('pathname:', u.pathname);     // //evil.com/steal
console.log('origin matches localhost:', u.origin === 'http://localhost');  // true
"
# Output:
# origin: http://localhost
# pathname: //evil.com/steal
# origin matches localhost: true
```

## Impact

An attacker can redirect users from a trusted application to an attacker-controlled domain. This enables:

- **Credential phishing**: Redirect to a lookalike login page to harvest credentials
- **OAuth token theft**: In OAuth flows using `redirectBack()`, steal authorization codes by redirecting to an attacker's callback
- **Trust exploitation**: Users see the initial link points to the trusted domain, lowering suspicion

The vulnerability requires no authentication and affects any endpoint using `redirectBack()`.

## Recommended Fix

Sanitize the extracted pathname to prevent protocol-relative URLs. In `src/utils/response.ts`, after extracting the pathname from the referer:

```typescript
export function redirectBack(
  event: H3Event,
  opts: { fallback?: string; status?: number; allowQuery?: boolean } = {},
): HTTPResponse {
  const referer = event.req.headers.get("referer");
  let location = opts.fallback ?? "/";
  if (referer && URL.canParse(referer)) {
    const refererURL = new URL(referer);
    if (refererURL.origin === event.url.origin) {
      let pathname = refererURL.pathname;
      // Prevent protocol-relative open redirect (e.g., "//evil.com")
      if (pathname.startsWith("//")) {
        pathname = "/" + pathname.replace(/^\/+/, "");
      }
      location = pathname + (opts.allowQuery ? refererURL.search : "");
    }
  }
  return redirect(location, opts.status);
}
```

## References
- https://github.com/h3js/h3/security/advisories/GHSA-fp4x-ggrf-wmc6
- https://github.com/h3js/h3/commit/459a1c6593365b0810e9c502df7c3e82837321d7
- https://github.com/h3js/h3
- https://github.com/h3js/h3/releases/tag/v2.0.1-rc.18
