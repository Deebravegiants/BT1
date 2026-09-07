# [M] hono: AWS Lambda adapter merges multiple `Set-Cookie` headers into one value, dropping cookies on ALB single-header and Lattice

## Summary
Severity: Medium
Advisory: GHSA-j6c9-x7qj-28xf
CVE: CVE-2026-54287
CWE: CWE-116
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-j6c9-x7qj-28xf
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.25

## Details
### Summary

On AWS Lambda, the ALB single-header response and the VPC Lattice v2 response join multiple `Set-Cookie` headers into one comma-separated value. Because commas also appear inside cookie attributes (for example `Expires` dates), clients cannot split the value back into individual cookies and silently drop or misparse them.

### Details

Per RFC 6265, each cookie must be its own `Set-Cookie` header line, and commas may appear inside attribute values. Joining cookies with `", "` collides with those commas, producing a value that clients cannot reliably split. Only ALB single-header mode and VPC Lattice v2 are affected; API Gateway v1/v2 and ALB with multi-value headers enabled already use an array and are unaffected.

### Impact

A client may receive only one of the cookies, a malformed cookie, or none. Session, CSRF, or preference cookies can silently fail to apply, breaking sessions or forcing re-authentication. This affects applications that set multiple cookies per response and run on AWS Lambda behind an ALB in single-header mode (the default) or VPC Lattice v2.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-j6c9-x7qj-28xf
- https://nvd.nist.gov/vuln/detail/CVE-2026-54287
- https://github.com/honojs/hono
