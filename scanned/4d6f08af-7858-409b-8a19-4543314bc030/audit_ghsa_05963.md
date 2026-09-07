# [M] undici vulnerable to CRLF Injection via blob-like body 'type' property

## Summary
Severity: Medium
Advisory: GHSA-m8rv-5g2x-5cg5
CVE: CVE-2026-15157
CWE: CWE-93
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-m8rv-5g2x-5cg5
Type: github-advisory

## Affected
- npm: `undici` — affected >=0 <6.28.0
- npm: `undici` — affected >=7.0.0 <7.29.0
- npm: `undici` — affected >=8.0.0 <8.9.0

## Details
### Impact

When an application passes a duck-typed blob-like body to undici's HTTP/1.1 dispatcher (via `request()`, `stream()`, `pipeline()`, or `dispatch()`) with a `.type` derived from untrusted input, an attacker can inject CRLF sequences (`\r\n`) to append arbitrary HTTP headers and potentially smuggle a second request past the upstream.

The vulnerable branch in `lib/dispatcher/client-h1.js` pushes `body.type` directly into the outgoing headers with no validation, while every other header path in undici goes through `isValidHeaderValue()`:

```javascript
} else if (util.isBlobLike(body) && request.contentType == null && body.type) {
  headers.push('content-type', body.type)  // bypasses isValidHeaderValue()
}
```

The bug requires a hand-rolled duck-typed blob object or a Blob subclass with a controlled `.type`. Native `Blob` is safe because its constructor strips CRLF from `.type`. `fetch()` is unaffected because it validates via the `Headers` class. Ecosystem consumers that build duck-typed blob shapes from user input include `form-data-encoder`, `formdata-polyfill`, and `formdata-node`.

Same defect class as `CVE-2022-35948` (explicit `content-type` sink, fixed in undici 5.8.2) and `CVE-2026-1527` (`upgrade` option sink, fixed in 6.24.0 / 7.24.0), both closed by adding `isValidHeaderValue()` on their respective sinks. This branch was missed.

### Patches

Patched in undici v6.28.0, v7.29.0, and v8.9.0. Users should upgrade to one of these versions or later.

### Workarounds

- Set an explicit, validated `content-type` header on the request options (skips the vulnerable branch).
- Use a native `Blob` (or `fetch-blob`) instead of a hand-rolled duck-typed object.
- Reject control characters in the MIME type before assigning it to `.type`.
- Use `fetch()` instead of the non-`fetch` APIs.

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-m8rv-5g2x-5cg5
- https://nvd.nist.gov/vuln/detail/CVE-2026-15157
- https://github.com/nodejs/undici/commit/33928bc24f742ea8422ed90d17f2e0cc83e4d09d
- https://github.com/nodejs/undici/commit/740a0b7c173cb4a83a5b693e96e8f3a116cfc400
- https://github.com/nodejs/undici/commit/7d3cf924c262c486bc77f951348f4e5c847b7b42
- https://cna.openjsf.org/security-advisories.html
- https://github.com/nodejs/undici
- https://github.com/nodejs/undici/releases/tag/v6.28.0
- https://github.com/nodejs/undici/releases/tag/v7.29.0
- https://github.com/nodejs/undici/releases/tag/v8.9.0
