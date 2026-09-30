# [M] Hono: bodyLimit() can be bypassed for chunked / unknown-length requests

## Summary
Severity: Medium
Advisory: GHSA-9vqf-7f2p-gf9v
CVE: CVE-2026-44456
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-9vqf-7f2p-gf9v
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.16

## Details
## Summary

`bodyLimit()` does not reliably enforce `maxSize` for requests without a usable `Content-Length` (e.g. `Transfer-Encoding: chunked`). Oversized requests can reach handlers and return `200` instead of `413`.

## Details

For chunked / unknown-length requests, `bodyLimit()` wraps the body in a stream that counts bytes asynchronously, then runs the handler before the size decision is final. The `413` is only applied afterwards by checking `c.error`.

This lets the limit be bypassed when:

- the handler does not read the body,
- the handler reads only the first chunk(s) and returns, or
- the handler reads the body but swallows the read error in `try/catch`.

In all three cases the handler returns `200` before the limit check completes (or its result is observed).

The fix is to enforce the size decision before `next()` runs, instead of retrofitting the response via `c.error` afterwards.

## Impact

Applications relying on `bodyLimit()` as a hard boundary can be bypassed: oversized chunked requests can reach handler logic and return successful responses. Per-request data exposure is bounded by `maxSize`, but the documented guarantee — "oversized requests are rejected before business logic runs" — does not hold.

## Credits

- @lalalala5678 (slow chunked / early return variants)
- @Jvr2022 (error handling bypass)

## References
- https://github.com/honojs/hono/security/advisories/GHSA-9vqf-7f2p-gf9v
- https://nvd.nist.gov/vuln/detail/CVE-2026-44456
- https://github.com/honojs/hono
