# [M] H3: Unbounded Chunked Cookie Count in Session Cleanup Loop may Lead to Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-q5pr-72pq-83v3
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-q5pr-72pq-83v3
Type: github-advisory

## Affected
- npm: `h3` — affected >=2.0.0-beta.4 <2.0.1-rc.18

## Details
## Summary

The `setChunkedCookie()` and `deleteChunkedCookie()` functions in h3 trust the chunk count parsed from a user-controlled cookie value (`__chunked__N`) without any upper bound validation. An unauthenticated attacker can send a single request with a crafted cookie header (e.g., `Cookie: h3=__chunked__999999`) to any endpoint using sessions, causing the server to enter an O(n²) loop that hangs the process.

## Details

The chunked cookie system stores large cookie values by splitting them into numbered chunks. The main cookie stores a sentinel value `__chunked__N` indicating how many chunks exist. When setting a new chunked cookie, the code cleans up any previous chunks that are no longer needed.

The vulnerability is in `getChunkedCookieCount()` at `src/utils/cookie.ts:244-249`:

```typescript
function getChunkedCookieCount(cookie: string | undefined): number {
  if (!cookie?.startsWith(CHUNKED_COOKIE)) {
    return Number.NaN;
  }
  return Number.parseInt(cookie.slice(CHUNKED_COOKIE.length));
  // No upper bound check — attacker controls this value
}
```

This value is consumed without validation in the cleanup loop of `setChunkedCookie()` at `src/utils/cookie.ts:182-190`:

```typescript
const previousCookie = getCookie(event, name); // reads from request headers
if (previousCookie?.startsWith(CHUNKED_COOKIE)) {
  const previousChunkCount = getChunkedCookieCount(previousCookie);
  if (previousChunkCount > chunkCount) {
    for (let i = chunkCount; i <= previousChunkCount; i++) {
      deleteCookie(event, chunkCookieName(name, i), options);
      // Each deleteCookie → setCookie → scans ALL existing set-cookie headers
    }
  }
}
```

The same issue exists in `deleteChunkedCookie()` at `src/utils/cookie.ts:227-232`:

```typescript
const chunksCount = getChunkedCookieCount(mainCookie);
if (chunksCount >= 0) {
  for (let i = 0; i < chunksCount; i++) {
    deleteCookie(event, chunkCookieName(name, i + 1), serializeOptions);
  }
}
```

**The exploit chain through sessions:**

1. Attacker sends `Cookie: h3=__chunked__999999` to any session-using endpoint
2. `getSession()` (`src/utils/session.ts:83`) calls `getChunkedCookie(event, "h3")` (line 124)
3. `getChunkedCookie()` returns `undefined` — the early return at line 153 fires because no actual chunk cookies (e.g., `h3.1`) exist in the request
4. Since `sealedSession` is undefined, `session.id` remains empty (line 140), triggering `updateSession()` (line 143)
5. `updateSession()` calls `setChunkedCookie()` with the newly sealed session value (line 179)
6. Inside `setChunkedCookie()`, `getCookie(event, name)` re-reads the original request cookie `__chunked__999999` at line 182
7. `previousChunkCount` = 999999, `chunkCount` = 1 (new sealed session is small)
8. The cleanup loop runs 999,998 iterations, each calling `deleteCookie()` → `setCookie()`
9. Each `setCookie()` call reads ALL existing `set-cookie` response headers via `getSetCookie()` (line 91) and iterates through them for deduplication (lines 100-106)
10. This creates O(n²) complexity — approximately 10¹² operations for n=999999

**Key observation:** While `getChunkedCookie()` has an early-return optimization (line 153) that prevents it from looping on missing chunks, the cleanup loops in `setChunkedCookie()` and `deleteChunkedCookie()` have no such protection and run unconditionally for the full claimed chunk count.

## PoC

**Prerequisites:** An h3 application with any endpoint using `getSession()` or `useSession()`.

Example minimal server:

```typescript
import { H3 } from "h3";
import { getSession } from "h3";

const app = new H3();

app.get("/dashboard", async (event) => {
  const session = await getSession(event, {
    password: "my-secret-password-at-least-32-chars-long!",
  });
  return { user: session.data.user || "anonymous" };
});

export default app;
```

**Attack (single request, no authentication):**

```bash
# This single request will hang the server process
curl -H 'Cookie: h3=__chunked__999999' http://localhost:3000/dashboard
```

For a less extreme but still impactful test:

```bash
# ~100K iterations — will take several seconds and block all other requests
curl -H 'Cookie: h3=__chunked__100000' http://localhost:3000/dashboard
```

The `deleteChunkedCookie()` path is exploitable via `clearSession()`:

```typescript
app.post("/logout", async (event) => {
  await clearSession(event, {
    password: "my-secret-password-at-least-32-chars-long!",
  });
  return { ok: true };
});
```

```bash
curl -X POST -H 'Cookie: h3=__chunked__999999' http://localhost:3000/logout
```

## Impact

- **Complete Denial of Service**: A single unauthenticated request with a 27-byte cookie header can hang the server process indefinitely. Node.js is single-threaded, so this blocks all request handling.
- **No authentication required**: The attack only requires the ability to send HTTP requests with a crafted cookie header.
- **Minimal attacker effort**: The payload is trivially small (`Cookie: h3=__chunked__999999`), making it easy to automate or repeat.
- **Wide attack surface**: Any endpoint in the application that uses `getSession()`, `useSession()`, or `clearSession()` is vulnerable. Session usage is extremely common in web applications.
- **Amplification**: The ratio of attacker input (27 bytes) to server work (billions of operations) is extreme.

## Recommended Fix

Add a maximum chunk count constant and validate in `getChunkedCookieCount()`:

```typescript
const MAX_CHUNKED_COOKIE_COUNT = 100;

function getChunkedCookieCount(cookie: string | undefined): number {
  if (!cookie?.startsWith(CHUNKED_COOKIE)) {
    return Number.NaN;
  }
  const count = Number.parseInt(cookie.slice(CHUNKED_COOKIE.length));
  if (Number.isNaN(count) || count < 0 || count > MAX_CHUNKED_COOKIE_COUNT) {
    return Number.NaN;
  }
  return count;
}
```

This clamps the parsed count at a safe maximum. Since each chunk can hold ~4000 bytes and 100 chunks would allow ~400KB of cookie data (far beyond any practical limit), `MAX_CHUNKED_COOKIE_COUNT = 100` is generous while eliminating the DoS vector.

Additionally, the callers should be updated to handle `NaN` safely. The cleanup loop in `setChunkedCookie()` already handles this correctly since `NaN > chunkCount` is false, so the loop won't execute. The `deleteChunkedCookie()` loop also handles it since `NaN >= 0` is false.

## References
- https://github.com/h3js/h3/security/advisories/GHSA-q5pr-72pq-83v3
- https://github.com/h3js/h3/commit/399257cb406fbeda313d88c1e288a15124fc82af
- https://github.com/h3js/h3
- https://github.com/h3js/h3/releases/tag/v2.0.1-rc.18
