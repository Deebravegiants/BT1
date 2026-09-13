# [M] hono: Body Limit Middleware can be bypassed on AWS Lambda by understating `Content-Length`

## Summary
Severity: Medium
Advisory: GHSA-rv63-4mwf-qqc2
CVE: CVE-2026-54288
CWE: CWE-345
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-rv63-4mwf-qqc2
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.25

## Details
### Summary

The Body Limit Middleware trusts the request's `Content-Length` header to decide whether a body is within the limit. On AWS Lambda (API Gateway v1/v2, ALB, VPC Lattice, and Lambda@Edge) the body is delivered fully buffered and the adapter builds the request with the client-declared `Content-Length`, which need not match the actual payload. A client can declare a tiny `Content-Length` while sending a much larger body, slipping past the limit.

### Details

When `Content-Length` is present and `Transfer-Encoding` is absent, the middleware compares the declared value against the limit and passes the request through if it is small enough. On standards-based runtimes the transport enforces that `Content-Length` matches the body, so this is safe. The Lambda adapters instead reconstruct the request from a buffered payload and copy the client's `Content-Length` verbatim, so the declared length and the real body size are decoupled.

This issue affects applications deployed on AWS Lambda that rely on the Body Limit Middleware to cap request body size.

### Impact

The declared body-size limit can be bypassed: a handler reads a payload larger than the configured maximum. Processing the oversized payload (large JSON, multipart, etc.) consumes additional CPU and memory per request. The payload remains bounded by the platform's request size limits, and Lambda isolates invocations, so the impact is increased per-request resource usage rather than full denial of service. This affects applications deployed on AWS Lambda that use the Body Limit Middleware.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-rv63-4mwf-qqc2
- https://nvd.nist.gov/vuln/detail/CVE-2026-54288
- https://github.com/honojs/hono
