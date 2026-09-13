# [H] undici vulnerable to cross-user information disclosure and parse-time crash via degenerate private cache directives

## Summary
Severity: High
Advisory: GHSA-4cwx-7wf7-3272
CVE: CVE-2026-13697
CWE: CWE-200, CWE-248, CWE-525
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-4cwx-7wf7-3272
Type: github-advisory

## Affected
- npm: `undici` — affected >=7.0.0 <7.29.0
- npm: `undici` — affected >=8.0.0 <8.9.0

## Details
### Summary

Two issues in undici's cache interceptor, both fixed by the same patch on `lib/util/cache.js`:

1. **Shared-cache disclosure:** Responses with malformed qualified `Cache-Control: private` directives such as `private=""` or `private=","` can be incorrectly stored in the default shared cache, then served to a later caller with the same cache key.
2. **Parse-time crash:** Mixed unqualified-and-qualified `private` directives in the same header (such as `public, max-age=60, private, private="hdr"`) cause an uncaught `TypeError` in the cache-control parser, terminating the request.

### Impact

#### Shared-cache disclosure

Applications using `interceptors.cache()` in shared mode may cache a user-specific response and serve it to a later caller with the same cache key. This can disclose private response bodies and headers, including `Set-Cookie`.

Required conditions:

- the cache interceptor is enabled in shared mode, including the default configuration;
- an upstream returns a malformed directive such as `Cache-Control: public, max-age=300, private=""`;
- another request later matches the same cache key, without a separating `Vary` header.

#### Parse-time crash

Applications using `interceptors.cache()` against an upstream that returns a `Cache-Control` header combining unqualified `private` with qualified `private="..."` see an uncaught `TypeError: output.private.concat is not a function` during response handling. The request rejects; depending on the consumer's error handling, the process may exit.

### Details

`private=""` is parsed as `{ private: [''] }`. The shared-cache guard only rejects `private === true`, so the response can be stored. When served from cache, the previous user's body and headers may be returned to a different user.

For the crash variant, an unqualified `private` directive sets `output.private = true`, then a subsequent qualified `private="hdr"` directive attempts `output.private.concat(['hdr'])`, which throws because boolean has no `concat` method.

The patch routes the qualified-directive path through a shared helper that normalizes empty-after-trim arrays to `true` and preserves existing `true` values, closing both vectors.

### Patches

Upgrade to `undici` 7.29.0 or 8.9.0. Both releases fix the qualified `private` directive handling that caused the shared-cache storage and the parser crash.

### Workarounds

Until patched, avoid shared `interceptors.cache()` for user-specific responses, use `type: 'private'`, or disable caching for affected origins.

### Credit

Disclosure variant reported by @h0rk1p via HackerOne report [#3817497](https://hackerone.com/reports/3817497).

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-4cwx-7wf7-3272
- https://nvd.nist.gov/vuln/detail/CVE-2026-13697
- https://github.com/nodejs/undici/commit/4fe5bc5fefe5ac81a200fc8e1cf84b8bf8464451
- https://cna.openjsf.org/security-advisories.html
- https://github.com/nodejs/undici
- https://github.com/nodejs/undici/releases/tag/v7.29.0
- https://github.com/nodejs/undici/releases/tag/v8.9.0
