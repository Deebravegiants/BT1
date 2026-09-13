# [M] Hono: API Gateway v1 adapter can drop a distinct repeated request header value during de-duplication

## Summary
Severity: Medium
Advisory: GHSA-xgm2-5f3f-mvvc
CVE: CVE-2026-59897
CWE: CWE-348
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-xgm2-5f3f-mvvc
Type: github-advisory

## Affected
- npm: `hono` — affected >=4.3.3 <4.12.27

## Details
### Summary

The AWS API Gateway v1 adapter can drop a distinct repeated request header value. When a header appears multiple times, the adapter de-duplicates values using a substring comparison instead of an exact match, so a value that is a substring of another value of the same header is omitted (for example, `203.0.113.1` is dropped when another value is `203.0.113.10`).

### Details

A repeated request header carries an ordered list of values. Middleware or application logic that depends on the complete list — such as IP restriction that walks the `X-Forwarded-For` chain, rate limiting, audit logging, or proxy-chain validation — can therefore receive incomplete data that differs from what the client actually sent.

This issue arises on deployments using the AWS API Gateway v1 adapter (the same pattern also affects the VPC Lattice adapter), for requests that contain the same header more than once.

### Impact

An attacker can craft repeated header values so that one value is omitted before the application sees the request. Where a security or routing decision relies on the full chain, this can alter that decision.

This affects applications deployed through Hono's AWS API Gateway v1 (or VPC Lattice) adapter that rely on the complete set of repeated request header values.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-xgm2-5f3f-mvvc
- https://nvd.nist.gov/vuln/detail/CVE-2026-59897
- https://github.com/honojs/hono/commit/aa921770d09bc35970362d5a2630a878f6d982fd
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v4.12.27
