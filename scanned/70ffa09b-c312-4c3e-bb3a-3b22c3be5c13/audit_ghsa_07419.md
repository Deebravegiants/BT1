# [H] blaze: Chunked-body trailer fields promoted into Request.headers in blaze-server (front-end header-sanitization bypass)

## Summary
Severity: High
Advisory: GHSA-46q4-43ph-c6fr
CVE: CVE-2026-73495
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-46q4-43ph-c6fr
Type: github-advisory

## Affected
- Maven: `org.http4s:blaze-http_2.13` — affected >=0 <0.23.18
- Maven: `org.http4s:blaze-http_2.12` — affected >=0 <0.23.18
- Maven: `org.http4s:blaze-http_3` — affected >=0 <0.23.18
- Maven: `org.http4s:blaze-http_3` — affected >=1.0.0-M1 <1.0.0-M42
- Maven: `org.http4s:blaze-http_2.13` — affected >=1.0.0-M1 <1.0.0-M42

## Details
### Summary
  blaze-server can merge HTTP/1.1 chunked-body trailer fields into `Request.headers`. Because trailer fields are attacker-controlled, an unauthenticated remote client can inject arbitrary header names/values (e.g. `X-Forwarded-For`, internal-auth headers) that a fronting proxy sanitized from the request-header section, bypassing header-based trust decisions in the application.

  ### Impact
  Any http4s application using `BlazeServerBuilder` over HTTP/1.1 whose routes or middleware trust proxy-set headers (e.g., `X-Forwarded-For`, `X-Real-IP`, `X-Forwarded-Host`, org-internal auth headers) is affected. Where a fronting proxy strips/normalizes those headers but forwards chunked bodies with trailers intact, an attacker can spoof client IP for allow-lists/rate-limits/audit, forge the `https` scheme, or inject internal-auth headers. A promoted `Connection: close` trailer is also honored, allowing attacker-controlled termination of pooled backend connections.

  ### Workarounds
  Deploy behind a proxy that removes trailer fields (or rejects requests that use trailers) before forwarding; until patched, avoid trust decisions based on headers that a proxy is relied upon to sanitize.

## References
- https://github.com/http4s/blaze/security/advisories/GHSA-46q4-43ph-c6fr
- https://github.com/http4s/blaze/commit/ef3e666c146cfc16cb6603f1fc3c464daab4a24f
- https://github.com/http4s/blaze
- https://github.com/http4s/blaze/releases/tag/v0.23.18
- https://github.com/http4s/blaze/releases/tag/v1.0.0-M42
