# [M] Eclipse Jetty: Cross-Request Leakage for trailers on HTTP/1.1 keep-alive connections

## Summary
Severity: Medium
Advisory: GHSA-f4v5-65jj-pcr2
CVE: CVE-2026-10051
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-f4v5-65jj-pcr2
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=12.0.0 <12.0.36
- Maven: `org.eclipse.jetty:jetty-server` — affected >=12.1.0 <12.1.10

## Details
### Description

> FINDING — MEDIUM (HTTP/1.1 keep-alive connections with trailers)
> HttpConnection._trailers Cross-Request Leakage (Never Reset Between Requests)
> 
> Location:
>   jetty-core/jetty-server/src/main/java/org/eclipse/jetty/server/internal/
>   HttpConnection.java:107, 1157-1161, 1170
> 
> Detail:
>   _trailers (line 107) is a connection-scoped HttpFields.Mutable field.
>   parsedTrailer() (line 1157) populates it when request N carries HTTP trailers.
>   messageComplete() (line 1170) checks "if (_trailers != null)" — evaluates true
>   from request N's data — and stamps it onto request N+1.
> 
>   Grep confirms: ZERO occurrences of "_trailers = null" in entire HttpConnection.java.
> 
>   Scenario:
>     Request N:   POST /upload (trailers: X-Checksum: abc123)
>     Request N+1: GET  /data   (no trailers)
>     app: request.getTrailers() on N+1 → returns {X-Checksum: abc123} ← STALE
> 
>   Application logic branching on getTrailers() != null produces incorrect behavior.
>   Not cross-connection (same keep-alive connection only).
> 
>   More dangerous scenario: TOCTOU — trailer passes check, target swapped before use.

### Workarounds
Do not rely on HTTP request trailers for security-sensitive logic, or disable persistent connections by closing the connection after each HTTP/1.1 request.

## References
- https://github.com/jetty/jetty.project/security/advisories/GHSA-f4v5-65jj-pcr2
- https://nvd.nist.gov/vuln/detail/CVE-2026-10051
- https://github.com/jetty/jetty.project/pull/15162
- https://github.com/jetty/jetty.project/pull/15163
- https://github.com/jetty/jetty.project/commit/72206b3ea623cf7ed8729b47a83ee628ff10e8eb
- https://github.com/jetty/jetty.project/commit/dc27e8d3ab743fe27935ea2d8c41756eb6c5bae9
- https://github.com/jetty/jetty.project
- https://github.com/jetty/jetty.project/releases/tag/jetty-12.0.36
- https://github.com/jetty/jetty.project/releases/tag/jetty-12.1.10
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/119
