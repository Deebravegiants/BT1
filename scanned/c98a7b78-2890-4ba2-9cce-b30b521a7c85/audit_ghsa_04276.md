# [M] hono: Lambda@Edge adapter keeps only the last value of a repeated request header, dropping the rest

## Summary
Severity: Medium
Advisory: GHSA-wgpf-jwqj-8h8p
CVE: CVE-2026-54289
CWE: CWE-348
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-wgpf-jwqj-8h8p
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.25

## Details
### Summary

On AWS Lambda@Edge, CloudFront delivers a request header that appears more than once as several separate entries. The adapter writes each value with `Headers.set` instead of `Headers.append`, so every value overwrites the previous one and only the last reaches the application. Repeated request headers such as `X-Forwarded-For`, `Forwarded`, and `Via` are silently truncated to a single value.

### Details

A repeated request header carries an ordered list of values. The adapter iterates the list but overwrites on each step, keeping only the final value. Middleware that depends on the full list — for example IP restriction that walks the `X-Forwarded-For` chain, or auditing based on `Forwarded`/`Via` hops — receives incomplete data. The API Gateway adapter already appends repeated values and is not affected.

This issue arises only on Lambda@Edge deployments, for requests that contain the same header more than once.

### Impact

Request middleware sees only the last value of a repeated header instead of the full chain. For applications that base access control on the `X-Forwarded-For` chain, this can weaken or alter that decision; for auditing, hop history is lost. This affects applications deployed on AWS Lambda@Edge that rely on multi-value request headers.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-wgpf-jwqj-8h8p
- https://nvd.nist.gov/vuln/detail/CVE-2026-54289
- https://github.com/honojs/hono
