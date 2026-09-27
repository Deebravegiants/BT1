# [M] undici vulnerable to downstream response desynchronization via retry interceptor

## Summary
Severity: Medium
Advisory: GHSA-8xcm-r25x-g524
CVE: CVE-2026-16728
CWE: CWE-444
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-8xcm-r25x-g524
Type: github-advisory

## Affected
- npm: `undici` — affected >=0 <6.28.0
- npm: `undici` — affected >=7.0.0 <7.29.0
- npm: `undici` — affected >=8.0.0 <8.9.0

## Details
### Impact

Undici's `interceptors.retry()` can deliver a response whose body length does not match the `Content-Length` header exposed to the application after a retry or resume of a partial response. Applications that use `interceptors.retry()` and forward upstream response headers and bodies downstream, for example proxy or gateway applications, may emit an invalid HTTP response with a stale `Content-Length` header. This can lead to downstream response desynchronization, connection hangs, or response corruption in clients or intermediaries that rely on the forwarded framing metadata.

A malicious or faulty upstream can respond to a range request with a `206 Partial Content` response such as:

```http
Content-Range: bytes 0-99/300
Content-Length: 300
```

and then send only 99 bytes before closing the socket. `interceptors.retry()` can then retry with `Range: bytes=99-99`, receive the final byte, and deliver a 100-byte body to the application while the response headers still contain `Content-Length: 300` from the first response.

The bug requires `interceptors.retry()` to be enabled, an upstream that returns a partial response with a mismatched framing header, and a downstream forwarder that does not remove or recalculate `Content-Length`.

### Patches

Patched in undici v6.28.0, v7.29.0, and v8.9.0. Users should upgrade to one of these versions or later.

### Workarounds

- Disable `interceptors.retry()` for untrusted upstreams.
- Remove or recalculate `Content-Length` before forwarding a response body assembled or transformed by Undici.

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-8xcm-r25x-g524
- https://nvd.nist.gov/vuln/detail/CVE-2026-16728
- https://github.com/nodejs/undici/commit/1b5a5312c3a7d7a30c31bf0d000b39a8a2531e1c
- https://github.com/nodejs/undici/commit/2b3f749336d356bbbc50192f87f6cf7bc714721a
- https://github.com/nodejs/undici/commit/4a9dafb16ff43880cf590e6d9c2aeee25fbff6d7
- https://github.com/nodejs/undici/commit/4fd5a0c61e627f928b7003adc4ffe1e55ec63420
- https://github.com/nodejs/undici/commit/cba3a52ac2e7abcc4e656d82af8579ea82c2bb9e
- https://github.com/nodejs/undici/commit/e11a68ed4ff345c79402476f7a00d473443e318d
- https://hackerone.com/reports/3828685
- https://cna.openjsf.org/security-advisories.html
- https://github.com/nodejs/undici
- https://github.com/nodejs/undici/releases/tag/v6.28.0
- https://github.com/nodejs/undici/releases/tag/v7.29.0
- https://github.com/nodejs/undici/releases/tag/v8.9.0
