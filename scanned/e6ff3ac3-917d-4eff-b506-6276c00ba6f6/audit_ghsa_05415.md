# [H] h3 v1 has Request Smuggling (TE.TE) issue

## Summary
Severity: High
Advisory: GHSA-mp2g-9vg9-f4cg
CVE: CVE-2026-23527
CWE: CWE-444
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-01-15
Source: https://github.com/advisories/GHSA-mp2g-9vg9-f4cg
Type: github-advisory

## Affected
- npm: `h3` — affected >=0 <1.15.5

## Details
I was digging into h3 v1 (specifically v1.15.4) and found a critical HTTP Request Smuggling vulnerability.

Basically, `readRawBody` is doing a strict case-sensitive check for the Transfer-Encoding header. It explicitly looks for "chunked", but per the RFC, this header should be case-insensitive.

**The Bug**: If I send a request with Transfer-Encoding: ChuNked (mixed case), h3 misses it. Since it doesn't see "chunked" and there's no Content-Length, it assumes the body is empty and processes the request immediately.

This leaves the actual body sitting on the socket, which triggers a classic TE.TE Desync (Request Smuggling) if the app is running behind a Layer 4 proxy or anything that doesn't normalize headers (like AWS NLB or Node proxies).

**Vulnerable Code** (`src/utils/body.ts`):

```js
if (
    !Number.parseInt(event.node.req.headers["content-length"] || "") &&
    !String(event.node.req.headers["transfer-encoding"] ?? "")
      .split(",")
      .map((e) => e.trim())
      .filter(Boolean)
      .includes("chunked") // <--- This is the issue. "ChuNkEd" returns false here.
  ) {
    return Promise.resolve(undefined);
  }
```

I verified this locally:

- Sent a `Transfer-Encoding: ChunKed` request without a closing 0 chunk.
- Express hangs (correctly waiting for data).
- h3 responds immediately (vulnerable, thinks body is length 0).

**Impact**: Since H3/Nuxt/Nitro is often used in containerized setups behind TCP load balancers, an attacker can use this to smuggle requests past WAFs or desynchronize the socket to poison other users' connections.

**Fix**: Just need to normalize the header value before checking: ` .map((e) => e.trim().toLowerCase())`

## References
- https://github.com/h3js/h3/security/advisories/GHSA-mp2g-9vg9-f4cg
- https://nvd.nist.gov/vuln/detail/CVE-2026-23527
- https://github.com/h3js/h3/commit/618ccf4f37b8b6148bea7f36040471af45bfb097
- https://github.com/h3js/h3
- https://github.com/h3js/h3/releases/tag/v1.15.5
- https://simonkoeck.com/writeups/h3-transfer-encoding-request-smuggling
