# [M] h3: Double Decoding in `serveStatic` Bypasses `resolveDotSegments` Path Traversal Protection via `%252e%252e`

## Summary
Severity: Medium
Advisory: GHSA-72gr-qfp7-vwhw
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-72gr-qfp7-vwhw
Type: github-advisory

## Affected
- npm: `h3` — affected >=0 <1.15.9

## Details
## Summary

The `serveStatic` utility in h3 applies a redundant `decodeURI()` call to the request pathname after `H3Event` has already performed percent-decoding with `%25` preservation. This double decoding converts `%252e%252e` into `%2e%2e`, which bypasses `resolveDotSegments()` (since it checks for literal `.` characters, not percent-encoded equivalents). When the resulting asset ID is resolved by URL-based backends (CDN, S3, object storage), `%2e%2e` is interpreted as `..` per the URL Standard, enabling path traversal to read arbitrary files from the backend.

## Details

The vulnerability is a conflict between two decoding stages:

**Stage 1 — `H3Event` constructor** (`src/event.ts:65-69`):

```typescript
if (url.pathname.includes("%")) {
  url.pathname = decodeURI(
    url.pathname.includes("%25") ? url.pathname.replace(/%25/g, "%2525") : url.pathname,
  );
}
```

This correctly preserves `%25` sequences by escaping them before decoding. A request for `/%252e%252e/etc/passwd` produces `event.url.pathname` = `/%2e%2e/etc/passwd` — the `%25` was preserved so `%252e` became `%2e` (not `.`).

**Stage 2 — `serveStatic`** (`src/utils/static.ts:86-88`):

```typescript
const originalId = resolveDotSegments(
  decodeURI(withLeadingSlash(withoutTrailingSlash(event.url.pathname))),
);
```

This applies a **second** `decodeURI()`, which decodes `%2e` → `.`, producing `/../../../etc/passwd`. However, the decoding happens *inside* the `resolveDotSegments()` call argument — `decodeURI` runs first, then `resolveDotSegments` processes the result.

Wait — re-examining the flow more carefully:

1. Input pathname after event.ts: `/%2e%2e/%2e%2e/etc/passwd`
2. `decodeURI()` in static.ts converts `%2e` → `.`, producing: `/../../../etc/passwd`
3. `resolveDotSegments("/../../../etc/passwd")` **does** resolve `..` segments, clamping to `/etc/passwd`

The actual bypass is subtler. `decodeURI()` does **not** decode `%2e` — it only decodes characters that `encodeURI` would encode. Since `.` is never encoded by `encodeURI`, `%2e` is **not** decoded by `decodeURI()`. So the chain is:

1. Request: `/%252e%252e/%252e%252e/etc/passwd`
2. After event.ts decode: `/%2e%2e/%2e%2e/etc/passwd`
3. `decodeURI()` in static.ts: `/%2e%2e/%2e%2e/etc/passwd` (unchanged — `decodeURI` doesn't decode `%2e`)
4. `resolveDotSegments()` fast-returns at line 56 because `%2e` contains no literal `.` character:
   ```typescript
   if (!path.includes(".")) {
     return path;
   }
   ```
5. Asset ID `/%2e%2e/%2e%2e/etc/passwd` is passed to `getMeta()` and `getContents()` callbacks
6. URL-based backends resolve `%2e%2e` as `..` per RFC 3986 / URL Standard

The root cause is `resolveDotSegments()` only checks for literal `.` characters and does not account for percent-encoded dot sequences (`%2e`). The `decodeURI()` in static.ts is redundant (event.ts already decodes) but is not the direct cause — the real gap is that `%2e%2e` survives as a traversal payload through both decoding stages and `resolveDotSegments`.

## PoC

**1. Create a minimal h3 server with a URL-based static backend:**

```javascript
// server.mjs
import { H3, serveStatic } from "h3";
import { serve } from "srvx";

const app = new H3();

app.get("/**", (event) => {
  return serveStatic(event, {
    getMeta(id) {
      console.log("[getMeta] asset ID:", id);
      // Simulate URL-based backend (CDN/S3)
      const url = new URL(id, "https://cdn.example.com/static/");
      console.log("[getMeta] resolved URL:", url.href);
      return { type: "text/plain" };
    },
    getContents(id) {
      console.log("[getContents] asset ID:", id);
      const url = new URL(id, "https://cdn.example.com/static/");
      console.log("[getContents] resolved URL:", url.href);
      return `Fetched from: ${url.href}`;
    },
  });
});

serve({ fetch: app.fetch, port: 3000 });
```

**2. Send the double-encoded traversal request:**

```bash
curl -v 'http://localhost:3000/%252e%252e/%252e%252e/etc/passwd'
```

**3. Observe server logs:**

```
[getMeta] asset ID: /%2e%2e/%2e%2e/etc/passwd
[getMeta] resolved URL: https://cdn.example.com/etc/passwd
[getContents] asset ID: /%2e%2e/%2e%2e/etc/passwd
[getContents] resolved URL: https://cdn.example.com/etc/passwd
```

The `%2e%2e` sequences in the asset ID are resolved as `..` by the `URL` constructor, causing the backend URL to traverse from `/static/` to `/etc/passwd`.

## Impact

- **Arbitrary file read from backend storage:** An unauthenticated attacker can read files outside the intended static asset directory on any URL-based backend (CDN origins, S3 buckets, object storage, reverse-proxied file servers).
- **Sensitive data exposure:** Depending on the backend, this could expose configuration files, credentials, source code, or other tenants' data in shared storage.
- **Affected deployments:** Applications using `serveStatic` with callbacks that resolve asset IDs via URL construction (`new URL(id, baseUrl)` or equivalent). This is a common pattern for CDN proxying and cloud object storage backends. Filesystem-based backends using `path.join()` are not affected since `%2e%2e` is not resolved as a traversal sequence by filesystem APIs.

## Recommended Fix

The `resolveDotSegments()` function must account for percent-encoded dot sequences. Additionally, the redundant `decodeURI()` in `serveStatic` should be removed since `H3Event` already handles decoding.

**Fix 1 — Remove redundant `decodeURI` in `src/utils/static.ts:86-88`:**

```diff
  const originalId = resolveDotSegments(
-   decodeURI(withLeadingSlash(withoutTrailingSlash(event.url.pathname))),
+   withLeadingSlash(withoutTrailingSlash(event.url.pathname)),
  );
```

**Fix 2 — Harden `resolveDotSegments` in `src/utils/internal/path.ts:55-73` to handle percent-encoded dots:**

```diff
 export function resolveDotSegments(path: string): string {
-  if (!path.includes(".")) {
+  if (!path.includes(".") && !path.toLowerCase().includes("%2e")) {
     return path;
   }
   // Normalize backslashes to forward slashes to prevent traversal via `\`
-  const segments = path.replaceAll("\\", "/").split("/");
+  const segments = path.replaceAll("\\", "/")
+    .replaceAll(/%2e/gi, ".")
+    .split("/");
   const resolved: string[] = [];
```

Both fixes should be applied. Fix 1 removes the unnecessary double-decode. Fix 2 provides defense-in-depth by ensuring `resolveDotSegments` cannot be bypassed with percent-encoded dots regardless of the caller.

## References
- https://github.com/h3js/h3/security/advisories/GHSA-72gr-qfp7-vwhw
- https://github.com/h3js/h3
